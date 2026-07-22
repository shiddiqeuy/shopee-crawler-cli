"""Interactive CLI Menu module."""

import subprocess
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from shopee_cli import __version__
from shopee_cli.commands.analytics import run_analytics
from shopee_cli.commands.export import export_excel, list_export_jobs
from shopee_cli.commands.insight import run_insight

from shopee_cli.commands.search import run_search
from shopee_cli.commands.status import show_status

console = Console()


def run_menu(
    once: Annotated[
        bool,
        typer.Option("--once", help="Run menu action once and exit."),
    ] = False,
) -> None:
    """Run interactive menu for Shopee Market Research CLI."""
    while True:
        console.clear()
        _print_menu_header()
        _print_menu_options()

        try:
            choice = Prompt.ask(
                "\n[bold cyan]Pilih menu (1-8)[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                default="1",
            )
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Keluar dari menu.[/yellow]")
            break

        if choice == "1":
            _handle_search()
        elif choice == "2":
            _handle_browser()
        elif choice == "3":
            _handle_launch_chrome()
        elif choice == "4":
            _handle_analytics()
        elif choice == "5":
            _handle_export()
        elif choice == "6":
            _handle_insight()
        elif choice == "7":
            show_status()
        elif choice == "8":
            console.print("\n[green]Terima kasih telah menggunakan Shopee Market Research CLI![/green]")
            break

        if once:
            break

        console.print("\n[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            break


def _print_menu_header() -> None:
    panel = Panel(
        f"[bold magenta]Shopee Market Research CLI v{__version__}[/bold magenta]\n"
        "[dim]Local-first marketplace intelligence & analysis tool[/dim]",
        title="[bold yellow]UTAMA[/bold yellow]",
        border_style="cyan",
    )
    console.print(panel)


def _print_menu_options() -> None:
    table = Table(show_header=True, header_style="bold green")
    table.add_column("No", style="bold cyan", width=4)
    table.add_column("Perintah / Fitur", style="bold white")
    table.add_column("Keterangan", style="dim")

    table.add_row("1", "[Search] Search Shopee Keyword", "Ambil data produk dari pencarian Shopee")
    table.add_row("2", "[Browser] Browser Status & Connect", "Cek koneksi browser (main / isolated)")
    table.add_row("3", "[Chrome] Launch Chrome Debugger", "Jalankan Chrome dengan Remote Debugging (port 9222)")
    table.add_row("4", "[Analytics] Lihat Analytics Market", "Analisis statistik snapshot di database")
    table.add_row("5", "[Export] Export Data ke Excel", "Simpan snapshot hasil pencarian ke .xlsx")
    table.add_row("6", "[Insight] Generate AI Insight", "Buat laporan analisis pasar berbasis AI")
    table.add_row("7", "[Status] Status Aplikasi", "Cek konfigurasi & path database lokal")
    table.add_row("8", "[Exit] Keluar", "Tutup aplikasi")

    console.print(table)


def _handle_search() -> None:
    console.print("\n[bold cyan]--- Search Shopee Keyword ---[/bold cyan]")
    keyword = Prompt.ask("Masukkan kata kunci (contoh: kopi arabika)")
    if not keyword.strip():
        console.print("[red]Keyword tidak boleh kosong![/red]")
        return

    limit_str = Prompt.ask("Jumlah limit produk (1-200)", default="50")
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 50

    mode = Prompt.ask("Pilih mode browser (main/isolated)", choices=["main", "isolated"], default="main")

    try:
        from shopee_cli.browser.models import BrowserMode
        run_search(keyword=keyword, limit=limit, mode=BrowserMode(mode))
    except Exception as exc:
        console.print(f"[red]Gagal menjalankan search: {exc}[/red]")


def _handle_browser() -> None:
    console.print("\n[bold cyan]--- Browser Management ---[/bold cyan]")
    from shopee_cli.commands.browser import show_browser_status
    show_browser_status()


def _handle_launch_chrome() -> None:
    console.print("\n[bold cyan]--- Launch Chrome Debugger ---[/bold cyan]")
    if sys.platform == "win32":
        try:
            subprocess.Popen(["launch_chrome_debug.bat"], shell=True)
            console.print("[green]Menjalankan launch_chrome_debug.bat...[/green]")
        except Exception as exc:
            console.print(f"[red]Gagal menjalankan script: {exc}[/red]")
    else:
        console.print("Jalankan Chrome manual dengan perintah:")
        console.print("[yellow]google-chrome --remote-debugging-port=9222[/yellow]")


def _handle_analytics() -> None:
    console.print("\n[bold cyan]--- Market Analytics ---[/bold cyan]")
    keyword = Prompt.ask("Keyword (kosongkan untuk snapshot terbaru)", default="")
    kw_arg = keyword if keyword.strip() else None
    try:
        run_analytics(keyword=kw_arg)
    except Exception as exc:
        console.print(f"[red]Gagal melihat analytics: {exc}[/red]")


def _handle_export() -> None:
    console.print("\n[bold cyan]--- Export Excel ---[/bold cyan]")
    sub = Prompt.ask("Pilih aksi", choices=["excel", "jobs"], default="excel")
    if sub == "jobs":
        list_export_jobs()
    else:
        keyword = Prompt.ask("Keyword (kosongkan untuk snapshot terbaru)", default="")
        kw_arg = keyword if keyword.strip() else None
        try:
            export_excel(keyword=kw_arg)
        except Exception as exc:
            console.print(f"[red]Gagal export: {exc}[/red]")


def _handle_insight() -> None:
    console.print("\n[bold cyan]--- AI Insight Generator ---[/bold cyan]")
    keyword = Prompt.ask("Keyword (kosongkan untuk snapshot terbaru)", default="")
    provider = Prompt.ask("AI Provider", choices=["openai", "anthropic", "google", "openrouter", "deepseek", "ollama"], default="openai")
    kw_arg = keyword if keyword.strip() else None
    try:
        run_insight(keyword=kw_arg, provider=provider)
    except Exception as exc:
        console.print(f"[red]Gagal membuat insight: {exc}[/red]")
