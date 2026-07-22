# Shopee Market Research CLI

Local-first CLI tool that helps understand Shopee market conditions by collecting and analyzing publicly accessible marketplace information.

Created by Muhammad Shiddiq Azis

Purpose:
To understand Shopee market condition through structured market research and data analysis.

## Cara Pakai Singkat

Panduan ini untuk menjalankan project dari awal sampai menghasilkan laporan.

### 🚀 Cara Cepat (1-Klik Setup & Run)

Bagi Anda yang ingin langsung menjalankan aplikasi tanpa perlu setup manual:

#### Windows:
1. **Setup Otomatis**: Double-click `setup.bat` (atau jalankan `setup.bat` di terminal) untuk menginstall seluruh dependency dan browser Playwright.
2. **Menu Interaktif**: Double-click `run.bat` (atau ketik `python run.py`) untuk membuka menu navigasi interaktif.
3. **Chrome Debugger**: Double-click `launch_chrome_debug.bat` untuk membuka Google Chrome dengan Remote Debugging Port 9222 secara otomatis (diperlukan untuk mode `main`).

#### Linux / macOS:
```bash
./setup.sh    # Setup venv & dependencies
./run.sh      # Jalankan menu interaktif CLI
```

---

### 1. Manual Setup Project (Opsional)


Clone repo dan masuk ke folder project:

```bash
git clone https://github.com/shiddiqeuy/shopee-crawler-cli.git
cd shopee-crawler-cli
```

Install dependency:

```bash
python -m pip install -e .
```

Install browser Playwright jika ingin memakai mode browser terpisah:

```bash
python -m playwright install chromium
```

Cek apakah CLI sudah bisa dipakai:

```bash
shopee --help
shopee version
shopee status
```

### 2. Pilih Cara Pakai Browser

Ada 2 mode browser.

Mode `main` memakai Chrome utama yang sudah kamu buka sendiri. Chrome harus dijalankan dengan remote debugging:

```bash
chrome.exe --remote-debugging-port=9222
```

Mode `isolated` memakai profile browser khusus aplikasi di `data/browser-profile`:

```bash
shopee browser connect --mode isolated
```

Cek status browser:

```bash
shopee browser status
```

### 3. Ambil Data Pencarian Shopee

Contoh ambil data keyword:

```bash
shopee search "kopi arabika"
```

Batasi jumlah produk yang dikumpulkan:

```bash
shopee search "kopi arabika" --limit 50
```

Pilih mode browser:

```bash
shopee search "kopi arabika" --mode main
shopee search "kopi arabika" --mode isolated
```

Data hasil pencarian akan disimpan otomatis ke DuckDB di folder `data/database`.

### 4. Lihat Analytics di Terminal

Analisis snapshot terbaru:

```bash
shopee analytics
```

Analisis berdasarkan keyword:

```bash
shopee analytics --keyword "kopi arabika"
```

Analisis berdasarkan job tertentu:

```bash
shopee analytics --job-id srch_xxxxx
```

### 5. Export ke Excel

Export snapshot terbaru:

```bash
shopee export excel
```

Lihat daftar job yang bisa diexport:

```bash
shopee export jobs
```

Export berdasarkan keyword:

```bash
shopee export excel --keyword "kopi arabika"
```

File Excel akan masuk ke folder `data/exports`.

### 6. Buat Insight AI

Insight AI membaca hasil analytics yang sudah dihitung. AI tidak menghitung ulang angka dan tidak scraping Shopee.

Set API key sesuai provider yang dipakai, contoh OpenAI:

```bash
set OPENAI_API_KEY=isi_api_key_kamu
```

Buat laporan insight Markdown:

```bash
shopee insight --keyword "kopi arabika" --provider openai
```

Simpan ke file tertentu:

```bash
shopee insight --keyword "kopi arabika" --provider openai --output reports/kopi-arabika-insight.md
```

### Catatan Penting

- **Verifikasi Anti-Bot**: Aplikasi ini **belum berhasil/belum mendukung penyelesaian verifikasi anti-bot Shopee secara otomatis**. Jika Shopee menampilkan verifikasi anti-bot (seperti puzzle/slider CAPTCHA), Anda harus menggeser/menyelesaikannya secara manual di jendela browser yang terbuka.
- Tool ini hanya membaca data yang terlihat di halaman hasil pencarian Shopee.
- Tool ini tidak membuka halaman detail produk.
- Tool ini tidak melakukan login otomatis.
- Semua data disimpan lokal di komputer kamu.
- Gunakan secara wajar dan hormati aturan Shopee.

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

Search collection is limited to fields visible on Shopee search-result pages. Product-detail pages are not opened. The application does not automatically bypass anti-bot verification; any puzzle slider or CAPTCHA must be completed manually in the browser window. Every run is stored as a separate historical snapshot, and manual login or verification may occasionally be required. Collected fields depend on what Shopee displays on the page.

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

The workbook contains Summary, Search Results, and Analytics sheets. Missing values remain empty or Unknown, product rows preserve stored ranking order, and analytics are basic deterministic statistics only. Every historical snapshot can be exported separately.

## Analytics MVP

Analyze the latest completed search snapshot:

```bash
shopee analytics
```

Analyze a specific completed job:

```bash
shopee analytics --job-id srch_xxxxx
```

Analyze the latest completed snapshot for a keyword:

```bash
shopee analytics --keyword "kopi arabika"
```

Analytics are calculated only from collected database snapshots. No AI is used, and no assumptions are generated. Metrics are deterministic and traceable to stored search-result records.

## AI Insight Engine

Generate a Markdown market insight from structured analytics JSON:

```bash
shopee insight
```

Generate insight for a specific completed job:

```bash
shopee insight --job-id srch_xxxxx
```

Generate insight for the latest completed snapshot for a keyword:

```bash
shopee insight --keyword "kopi arabika"
```

Choose a provider and output file:

```bash
shopee insight --provider openai --output reports/kopi-arabika-insight.md
```

The AI analyzes structured analytics only. It does not scrape Shopee, does not access browser data, does not query raw DuckDB tables, and does not replace the Analytics Engine. The AI does not calculate metrics; it only interprets metrics already calculated by the deterministic analytics layer.

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
