# Shopee Market Research CLI

Local-first CLI tool that helps understand Shopee market conditions by collecting and analyzing publicly accessible marketplace information.

Created by Muhammad Shiddiq Azis

Purpose:
To understand Shopee market condition through structured market research and data analysis.

## Features

Planned features:

- CLI-based market research workflow
- Browser manager with Main Chrome and isolated profile modes
- Public marketplace information collection
- Product competition analysis
- Pricing landscape analysis
- Keyword opportunity research
- Local exports for research results

## Browser Modes

Main Chrome Mode:

- Connects to an already-running Chrome instance
- Uses a configurable Chrome DevTools Protocol endpoint
- Reuses the user's existing Shopee login when available
- Does not launch, close, or modify the main Chrome profile

Isolated Profile Mode:

- Uses a dedicated persistent browser profile in `data/browser-profile`
- Requires manual Shopee login once
- Preserves session data in the application profile
- Closes only the application-created browser context

Command examples:

```bash
shopee browser status
shopee browser connect --mode main
shopee browser connect --mode isolated
shopee browser tabs
shopee browser open-shopee
```

## Search Collector

Collect visible Shopee search-result product cards into local DuckDB snapshots.

Basic usage:

```bash
shopee search "kopi arabika"
```

Custom limit:

```bash
shopee search "kopi arabika" --limit 100
```

Choose browser mode:

```bash
shopee search "kopi arabika" --mode main
shopee search "kopi arabika" --mode isolated
```

Search collection is limited to fields visible on Shopee search-result pages. Product-detail pages are not opened. Every run is stored as a separate historical snapshot, and manual login or verification may occasionally be required. Collected fields depend on what Shopee displays on the page.

## Excel Export

Export an existing DuckDB search snapshot to an Excel workbook. Export does not rerun browser collection.

Export latest snapshot:

```bash
shopee export excel
```

Export by job ID:

```bash
shopee export excel --job-id srch_xxxxx
```

Export latest snapshot for a keyword:

```bash
shopee export excel --keyword "kopi arabika"
```

Custom output:

```bash
shopee export excel --output data/exports/kopi-arabika.xlsx
```

List available jobs:

```bash
shopee export jobs
```

The workbook contains exactly two sheets: Summary and Search Results. Missing values remain empty or Unknown, product rows preserve stored ranking order, and the Summary sheet contains basic descriptive statistics only. Every historical snapshot can be exported separately.

## Roadmap

- Project foundation and CLI commands
- Browser profile and collector setup
- Search collection workflow
- Shopee result parsing
- Analytics and reporting
- Export workflows

## Author

Muhammad Shiddiq Azis

## License

MIT
