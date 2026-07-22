"""Search product card parser."""

import re
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse

from playwright.sync_api import Error as PlaywrightError

from shopee_cli.browser.shopee import SHOPEE_HOME_URL, is_marketplace_url
from shopee_cli.collectors import selectors
from shopee_cli.collectors.models import SearchResult
from shopee_cli.normalization.price import (
    parse_discount_percentage,
    parse_price_range,
    parse_price_value,
)
from shopee_cli.normalization.sold import parse_rating, parse_sold_count
from shopee_cli.normalization.text import clean_text


def parse_product_card(
    card: object,
    rank: int,
    collected_at: datetime,
) -> SearchResult | None:
    """Parse one visible product card into a normalized result."""
    product_url = _extract_product_url(card)
    if not product_url or not is_marketplace_url(product_url):
        return None

    full_text = _safe_inner_text(card)
    product_name = _first_text(card, selectors.PRODUCT_NAME_SELECTORS)
    if not product_name:
        product_name = _infer_name_from_text(full_text)
    if not product_name:
        return None

    price_raw = _first_text(card, selectors.PRICE_SELECTORS) or _match_text(
        full_text,
        r"Rp\s*[\d.]+(?:\s*-\s*Rp?\s*[\d.]+)?",
    )
    original_price_raw = _first_text(card, selectors.ORIGINAL_PRICE_SELECTORS)
    discount_raw = _first_text(card, selectors.DISCOUNT_SELECTORS) or _match_text(
        full_text,
        r"\d{1,3}\s*%",
    )
    sold_raw = _first_text(card, selectors.SOLD_SELECTORS) or _match_text(
        full_text,
        r"\d+(?:[,.]\d+)?\s*(?:RB|K|JT|M)?\+?\s*(?:terjual|sold)",
    )
    rating_raw = _first_text(card, selectors.RATING_SELECTORS)

    price_min, price_max = parse_price_range(price_raw)
    return SearchResult(
        product_id=extract_product_id(product_url),
        rank=rank,
        product_name=product_name,
        product_url=canonicalize_product_url(product_url),
        image_url=_extract_image_url(card),
        price_raw=price_raw,
        price_min=price_min,
        price_max=price_max,
        original_price=parse_price_value(original_price_raw),
        discount_percentage=parse_discount_percentage(discount_raw),
        sold_raw=sold_raw,
        sold_count=parse_sold_count(sold_raw),
        rating=parse_rating(rating_raw),
        shop_name=_first_text(card, selectors.SHOP_SELECTORS),
        location=_first_text(card, selectors.LOCATION_SELECTORS),
        is_advertisement=_indicator_visible(card, selectors.AD_SELECTORS),
        is_mall=_indicator_visible(card, selectors.MALL_SELECTORS),
        is_preferred=_indicator_visible(card, selectors.PREFERRED_SELECTORS),
        collected_at=collected_at,
    )


def deduplicate_results(results: list[SearchResult]) -> list[SearchResult]:
    """Deduplicate results within one job and assign first-seen ranks."""
    deduplicated: list[SearchResult] = []
    seen: set[str] = set()
    for result in results:
        identity = result_identity(result)
        if identity in seen:
            continue
        seen.add(identity)
        deduplicated.append(result.model_copy(update={"rank": len(deduplicated) + 1}))
    return deduplicated


def result_identity(result: SearchResult) -> str:
    """Return a stable per-job product identity."""
    if result.product_id:
        return f"id:{result.product_id}"
    if result.product_url:
        return f"url:{canonicalize_product_url(result.product_url)}"
    return f"fallback:{result.product_name.lower()}:{result.shop_name or ''}"


def extract_product_id(url: str) -> str | None:
    """Extract a stable Shopee item ID from a product URL when available."""
    match = re.search(r"(?:-i\.|/product/)\d+[./](\d+)", url)
    return match.group(1) if match else None


def canonicalize_product_url(url: str) -> str:
    """Remove query and fragment parts from a product URL."""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def _extract_product_url(card: object) -> str | None:
    for selector in selectors.PRODUCT_LINK_SELECTORS:
        locator = _safe_locator(card, selector)
        if locator is None or _safe_count(locator) == 0:
            continue
        href = _safe_get_attribute(locator.first, "href")
        if href:
            return urljoin(SHOPEE_HOME_URL, href)
    href = _safe_get_attribute(card, "href")
    return urljoin(SHOPEE_HOME_URL, href) if href else None


def _extract_image_url(card: object) -> str | None:
    for selector in selectors.IMAGE_SELECTORS:
        locator = _safe_locator(card, selector)
        if locator is None or _safe_count(locator) == 0:
            continue
        src = _safe_get_attribute(locator.first, "src")
        if src:
            return src
    return None


def _first_text(card: object, selector_group: tuple[str, ...]) -> str | None:
    for selector in selector_group:
        locator = _safe_locator(card, selector)
        if locator is None or _safe_count(locator) == 0:
            continue
        text = clean_text(_safe_inner_text(locator.first))
        if text:
            return text
    return None


def _indicator_visible(card: object, selector_group: tuple[str, ...]) -> bool | None:
    for selector in selector_group:
        locator = _safe_locator(card, selector)
        if locator is not None and _safe_count(locator) > 0:
            return True
    return None


def _infer_name_from_text(text: str | None) -> str | None:
    if not text:
        return None
    for line in text.splitlines():
        cleaned = clean_text(line)
        if cleaned and not cleaned.startswith("Rp"):
            return cleaned
    return None


def _match_text(text: str | None, pattern: str) -> str | None:
    if not text:
        return None
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return clean_text(match.group(0)) if match else None


def _safe_locator(obj: object, selector: str) -> object | None:
    try:
        return obj.locator(selector)
    except (AttributeError, PlaywrightError):
        return None


def _safe_count(locator: object) -> int:
    try:
        return locator.count()
    except (AttributeError, PlaywrightError):
        return 0


def _safe_inner_text(obj: object) -> str | None:
    try:
        return obj.inner_text()
    except (AttributeError, PlaywrightError):
        return None


def _safe_get_attribute(obj: object, name: str) -> str | None:
    try:
        return obj.get_attribute(name)
    except (AttributeError, PlaywrightError):
        return None
