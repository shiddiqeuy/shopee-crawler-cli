"""Database schema migrations."""

from duckdb import DuckDBPyConnection


def initialize_search_schema(connection: DuckDBPyConnection) -> None:
    """Create search tables idempotently."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS search_jobs (
            job_id VARCHAR PRIMARY KEY,
            keyword VARCHAR NOT NULL,
            requested_limit INTEGER NOT NULL,
            collected_count INTEGER DEFAULT 0,
            browser_mode VARCHAR NOT NULL,
            sort_mode VARCHAR NOT NULL,
            source_url VARCHAR NOT NULL,
            status VARCHAR NOT NULL,
            started_at TIMESTAMP NOT NULL,
            finished_at TIMESTAMP,
            error_message VARCHAR
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS search_results (
            result_id VARCHAR PRIMARY KEY,
            job_id VARCHAR NOT NULL,
            product_id VARCHAR,
            rank INTEGER NOT NULL,
            product_name VARCHAR NOT NULL,
            product_url VARCHAR NOT NULL,
            image_url VARCHAR,
            price_raw VARCHAR,
            price_min BIGINT,
            price_max BIGINT,
            original_price BIGINT,
            discount_percentage INTEGER,
            sold_raw VARCHAR,
            sold_count BIGINT,
            rating DOUBLE,
            shop_name VARCHAR,
            location VARCHAR,
            is_advertisement BOOLEAN,
            is_mall BOOLEAN,
            is_preferred BOOLEAN,
            collected_at TIMESTAMP NOT NULL,
            FOREIGN KEY (job_id) REFERENCES search_jobs(job_id)
        )
        """
    )
