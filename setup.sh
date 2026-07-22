#!/usr/bin/env bash
set -e

echo "==================================================="
echo "  Shopee Market Research CLI - Setup Initializer"
echo "==================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 tidak ditemukan! Harap install Python 3.13+."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "[INFO] Membuat Virtual Environment (.venv)..."
    python3 -m venv .venv
    echo "[OK] Virtual Environment berhasil dibuat."
else
    echo "[INFO] Virtual Environment (.venv) sudah ada."
fi

source .venv/bin/activate

echo ""
echo "[INFO] Menginstall dependency project..."
pip install --upgrade pip
pip install -e .

echo ""
echo "[INFO] Menginstall Playwright Chromium Browser..."
python3 -m playwright install chromium || echo "[WARNING] Playwright install encountered an issue."

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[OK] File .env berhasil dibuat dari .env.example"
fi

echo ""
echo "==================================================="
echo "  SETUP SELESAI!"
echo "  Jalankan CLI dengan:"
echo "    ./run.sh menu"
echo "    ./run.sh search \"kopi\""
echo "==================================================="
