"""Analytics models."""

from pydantic import BaseModel, ConfigDict

from shopee_cli.collectors.models import SearchJob


class NumericSummary(BaseModel):
    """Numeric metric summary."""

    model_config = ConfigDict(frozen=True)

    minimum: float | None = None
    maximum: float | None = None
    average: float | None = None
    median: float | None = None
    count: int = 0
    missing: int = 0


class PriceAnalysis(NumericSummary):
    """Price analytics."""

    price_range: float | None = None
    q1: float | None = None
    q3: float | None = None


class SellerAnalysis(BaseModel):
    """Seller analytics."""

    model_config = ConfigDict(frozen=True)

    unique_shops: int
    mall_shops: int
    preferred_shops: int
    advertisement_products: int
    organic_products: int


class LocationAnalysis(BaseModel):
    """Location analytics."""

    model_config = ConfigDict(frozen=True)

    unique_locations: int
    top_locations: list[tuple[str, int]]


class ProductDistribution(BaseModel):
    """Product distribution by boolean flags."""

    model_config = ConfigDict(frozen=True)

    mall: int
    preferred: int
    advertisement: int
    unknown: int


class QualityMetrics(BaseModel):
    """Data quality metrics."""

    model_config = ConfigDict(frozen=True)

    missing_price: int
    missing_rating: int
    missing_sold: int
    missing_shop: int
    missing_location: int
    duplicate_products_removed: int


class AnalyticsReport(BaseModel):
    """Complete analytics report for one snapshot."""

    model_config = ConfigDict(frozen=True)

    job: SearchJob
    total_products: int
    price: PriceAnalysis
    sales: NumericSummary
    rating: NumericSummary
    seller: SellerAnalysis
    location: LocationAnalysis
    distribution: ProductDistribution
    quality: QualityMetrics
