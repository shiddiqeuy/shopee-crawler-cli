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
