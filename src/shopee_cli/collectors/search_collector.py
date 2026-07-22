"""Shopee search collector orchestration."""

from datetime import UTC, datetime
from urllib.parse import urlencode, urlparse

from playwright.sync_api import Error as PlaywrightError

from shopee_cli.browser.manager import BrowserManager
from shopee_cli.browser.models import BrowserMode
from shopee_cli.browser.shopee import SHOPEE_HOST
from shopee_cli.collectors import selectors
from shopee_cli.collectors.exceptions import (
    InvalidKeywordError,
    ProductCardNotFoundError,
    SearchPageLoadError,
    SearchVerificationRequiredError,
    UnsupportedSortModeError,
)
from shopee_cli.collectors.models import (
    SearchCollection,
    SearchJobStatus,
    SearchRequest,
    SearchResult,
    SearchSortMode,
)
from shopee_cli.collectors.parser import deduplicate_results, parse_product_card
from shopee_cli.collectors.scrolling import scroll_until_complete
from shopee_cli.logging.logger import get_logger

MIN_KEYWORD_LENGTH = 1
MAX_KEYWORD_LENGTH = 120
MIN_LIMIT = 1
MAX_LIMIT = 200
MIN_MAX_SCROLLS = 1
MAX_MAX_SCROLLS = 30

logger = get_logger(__name__)


def validate_keyword(keyword: str) -> str:
    """Validate and normalize a user search keyword."""
    normalized = keyword.strip()
    if len(normalized) < MIN_KEYWORD_LENGTH:
        msg = "Keyword must not be empty."
        raise InvalidKeywordError(msg)
    if len(normalized) > MAX_KEYWORD_LENGTH:
        msg = f"Keyword must be {MAX_KEYWORD_LENGTH} characters or fewer."
        raise InvalidKeywordError(msg)
    return normalized


def validate_limit(limit: int) -> int:
    """Validate requested result limit."""
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        msg = f"Limit must be between {MIN_LIMIT} and {MAX_LIMIT}."
        raise ValueError(msg)
    return limit


def validate_max_scrolls(max_scrolls: int) -> int:
    """Validate maximum scroll count."""
    if max_scrolls < MIN_MAX_SCROLLS or max_scrolls > MAX_MAX_SCROLLS:
        msg = f"Max scrolls must be between {MIN_MAX_SCROLLS} and {MAX_MAX_SCROLLS}."
        raise ValueError(msg)
    return max_scrolls


def build_search_url(keyword: str, sort_mode: SearchSortMode = SearchSortMode.RELEVANCE) -> str:
    """Build a safe Shopee marketplace search URL."""
    normalized = validate_keyword(keyword)

    if sort_mode == SearchSortMode.LATEST:
        sort_by = "ctime"
    elif sort_mode == SearchSortMode.PRICE_LOW or sort_mode == SearchSortMode.PRICE_HIGH:
        sort_by = "price"
    else:
        sort_by = "sales"

    params = {
        "keyword": normalized,
        "page": 0,
        "sortBy": sort_by,
    }
    if sort_mode == SearchSortMode.PRICE_LOW:
        params["order"] = "asc"
    elif sort_mode == SearchSortMode.PRICE_HIGH:
        params["order"] = "desc"

    query = urlencode(params)
    url = f"https://{SHOPEE_HOST}/search?{query}"
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != SHOPEE_HOST:
        msg = "Search URL must use the Shopee marketplace domain."
        raise SearchPageLoadError(msg)
    return url


def create_search_request(
    keyword: str,
    limit: int,
    browser_mode: BrowserMode,
    sort_mode: SearchSortMode,
    max_scrolls: int,
) -> SearchRequest:
    """Create a validated search request."""
    normalized_keyword = validate_keyword(keyword)
    requested_limit = validate_limit(limit)
    scroll_limit = validate_max_scrolls(max_scrolls)
    source_url = build_search_url(normalized_keyword, sort_mode)
    return SearchRequest(
        keyword=normalized_keyword,
        requested_limit=requested_limit,
        browser_mode=browser_mode,
        sort_mode=sort_mode,
        max_scrolls=scroll_limit,
        source_url=source_url,
    )


class SearchCollector:
    """Collect visible Shopee search-result product cards."""

    def __init__(self, manager: BrowserManager) -> None:
        self._manager = manager

    def collect(self, request: SearchRequest) -> SearchCollection:
        """Collect visible product cards for a search request."""
        page = self._manager.get_or_open_shopee_page()
        try:
            page.goto(request.source_url, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightError as error:
            msg = "Shopee search results could not be loaded."
            raise SearchPageLoadError(msg) from error

        self._ensure_safe_page_state(page)

        def unique_count() -> int:
            return len(self._collect_visible_results(page, request.requested_limit))

        scroll_until_complete(
            page=page,
            get_unique_count=unique_count,
            requested_limit=request.requested_limit,
            max_scrolls=request.max_scrolls,
        )
        results = self._collect_visible_results(page, request.requested_limit)
        if not results and not self._has_no_results(page):
            msg = "Shopee product cards could not be identified on the search page."
            raise ProductCardNotFoundError(msg)

        return SearchCollection(
            request=request,
            results=results,
            status=SearchJobStatus.COMPLETED,
        )

    def _collect_visible_results(self, page: object, limit: int) -> list[SearchResult]:
        cards = self._product_cards(page)
        collected_at = datetime.now(UTC)
        results: list[SearchResult] = []
        for index in range(cards.count()):
            parsed = parse_product_card(cards.nth(index), index + 1, collected_at)
            if parsed is not None:
                results.append(parsed)

        return deduplicate_results(results)[:limit]

    def _product_cards(self, page: object) -> object:
        for selector in selectors.PRODUCT_CARD_SELECTORS:
            locator = page.locator(selector)
            if locator.count() > 0:
                return locator
        return page.locator(selectors.PRODUCT_CARD_SELECTORS[0])

    def _ensure_safe_page_state(self, page: object) -> None:
        page_url = getattr(page, "url", "")
        if self._has_selector(page, selectors.VERIFICATION_SELECTORS):
            msg = (
                "Manual Shopee verification is required before collection can continue."
            )
            raise SearchVerificationRequiredError(msg)
        if "/buyer/login" in page_url or "/user/login" in page_url or self._has_selector(page, selectors.LOGIN_SELECTORS):
            msg = "Shopee login appears inactive. Log in manually, then rerun search."
            raise SearchVerificationRequiredError(msg)
        if self._has_selector(page, selectors.TEMPORARY_ERROR_SELECTORS):
            msg = "Shopee returned a temporary error page. Retry later."
            raise SearchPageLoadError(msg)

    def _has_no_results(self, page: object) -> bool:
        return self._has_selector(page, selectors.NO_RESULTS_SELECTORS)

    def _has_selector(self, page: object, selector_group: tuple[str, ...]) -> bool:
        for selector in selector_group:
            try:
                if page.locator(selector).first.count() > 0:
                    return True
            except PlaywrightError as error:
                logger.warning(
                    "search_selector_failed",
                    selector=selector,
                    error=str(error),
                )
            except AttributeError as error:
                logger.warning(
                    "search_selector_failed",
                    selector=selector,
                    error=str(error),
                )
        return False
