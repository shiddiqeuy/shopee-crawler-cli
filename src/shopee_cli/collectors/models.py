"""Search collector models."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from shopee_cli.browser.models import BrowserMode


class SearchSortMode(StrEnum):
    """Supported CLI sort values."""

    RELEVANCE = "relevance"
    LATEST = "latest"
    TOP_SALES = "top-sales"
    PRICE_LOW = "price-low"
    PRICE_HIGH = "price-high"


class SearchJobStatus(StrEnum):
    """Search job statuses."""

    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchRequest(BaseModel):
    """Validated search request."""

    model_config = ConfigDict(frozen=True)

    keyword: str
    requested_limit: int
    browser_mode: BrowserMode
    sort_mode: SearchSortMode
    max_scrolls: int
    source_url: str


class SearchResult(BaseModel):
    """A normalized product card result."""

    model_config = ConfigDict(frozen=True)

    product_id: str | None = None
    rank: int
    product_name: str
    product_url: str
    image_url: str | None = None
    price_raw: str | None = None
    price_min: int | None = None
    price_max: int | None = None
    original_price: int | None = None
    discount_percentage: int | None = None
    sold_raw: str | None = None
    sold_count: int | None = None
    rating: float | None = None
    shop_name: str | None = None
    location: str | None = None
    is_advertisement: bool | None = None
    is_mall: bool | None = None
    is_preferred: bool | None = None
    collected_at: datetime


class SearchJob(BaseModel):
    """Search job metadata."""

    model_config = ConfigDict(frozen=True)

    job_id: str
    keyword: str
    requested_limit: int
    collected_count: int
    browser_mode: BrowserMode
    sort_mode: SearchSortMode
    source_url: str
    status: SearchJobStatus
    started_at: datetime
    finished_at: datetime | None = None
    error_message: str | None = None


class SearchCollection(BaseModel):
    """Completed in-memory search collection."""

    model_config = ConfigDict(frozen=True)

    request: SearchRequest
    results: list[SearchResult]
    status: SearchJobStatus
    error_message: str | None = None
