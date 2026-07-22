"""Export models."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from shopee_cli.collectors.models import SearchJob, SearchResult


class SummaryStats(BaseModel):
    """Basic descriptive statistics for a search snapshot."""

    model_config = ConfigDict(frozen=True)

    total_products: int
    products_with_price: int
    minimum_price: int | None
    maximum_price: int | None
    average_minimum_price: float | None
    median_minimum_price: float | None
    products_with_sold_data: int
    average_sold_count: float | None
    median_sold_count: float | None
    products_with_rating: int
    average_rating: float | None
    advertisement_count: int
    mall_product_count: int
    preferred_product_count: int
    unique_shops: int
    unique_locations: int
    missing_product_name: int
    missing_product_url: int
    missing_price: int
    missing_sold_data: int
    missing_rating: int
    missing_shop_name: int
    missing_location: int
    unknown_advertisement_status: int


class ExportSelection(BaseModel):
    """Selected export data."""

    model_config = ConfigDict(frozen=True)

    job: SearchJob
    results: list[SearchResult]


class ExportResult(BaseModel):
    """Excel export result."""

    model_config = ConfigDict(frozen=True)

    job: SearchJob
    output_path: Path
    sheet_count: int
    product_count: int
