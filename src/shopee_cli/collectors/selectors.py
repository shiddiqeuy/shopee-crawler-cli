"""Centralized Shopee search selectors."""

PRODUCT_CARD_SELECTORS = (
    "[data-sqe='item']",
    "li[data-sqe='item']",
    "div[data-sqe='item']",
    "a[href*='-i.']",
)

PRODUCT_LINK_SELECTORS = (
    "a[href*='-i.']",
    "a[href*='/product/']",
)

PRODUCT_NAME_SELECTORS = (
    "[data-testid='product-card-name']",
    "div[aria-label]",
)

IMAGE_SELECTORS = ("img",)
PRICE_SELECTORS = ("[data-testid='product-card-price']", "text=/^Rp/")
ORIGINAL_PRICE_SELECTORS = ("s", "del")
DISCOUNT_SELECTORS = ("text=/%/",)
SOLD_SELECTORS = ("text=/terjual/i", "text=/sold/i")
RATING_SELECTORS = ("[aria-label*='rating']", "text=/^[0-5][,.][0-9]$/")
SHOP_SELECTORS = ("[data-testid='product-card-shop-name']",)
LOCATION_SELECTORS = ("[data-testid='product-card-location']",)
AD_SELECTORS = ("text=/^Iklan$/i", "text=/^Ad$/i")
MALL_SELECTORS = ("text=/Mall/i",)
PREFERRED_SELECTORS = ("text=/Star/i", "text=/Preferred/i")
NO_RESULTS_SELECTORS = ("text=/Tidak ada hasil/i", "text=/No results/i")
LOGIN_SELECTORS = ("input[name='loginKey']", "text=/Log In/i", "text=/Masuk/i")
VERIFICATION_SELECTORS = (
    "text=/CAPTCHA/i",
    "text=/Verifikasi/i",
    "text=/Verification/i",
)
TEMPORARY_ERROR_SELECTORS = ("text=/Coba lagi/i", "text=/Try again/i")
