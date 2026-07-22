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


import socket


def _is_cdp_available(host: str = "127.0.0.1", port: int = 9222) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


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

    cdp_active = _is_cdp_available()
    if cdp_active:
        mode = "main"
        console.print("[bold green]✓ Menggunakan Chrome utama yang aktif (mode 'main').[/bold green]")
    else:
        mode = "isolated"
        console.print("[bold cyan]✓ Chrome Debugger (port 9222) tidak aktif. Menggunakan mode 'isolated'.[/bold cyan]")

    try:
        from shopee_cli.browser.models import BrowserMode
        run_search(keyword=keyword, limit=limit, mode=BrowserMode(mode))
    except (typer.Exit, SystemExit):
        if mode == "main" and not _is_cdp_available():
            console.print("\n[yellow]Gagal terhubung ke Chrome utama.[/yellow]")
            console.print("[bold yellow]Solusi:[/bold yellow]")
            console.print(" 1. Jalankan menu 3 ('[bold green]Launch Chrome Debugger[/bold green]') untuk membuka Chrome.")
            console.print(" 2. ATAU gunakan mode '[bold cyan]isolated[/bold cyan]' yang tidak memerlukan Chrome terpisah.")
    except Exception as exc:
        console.print(f"[red]Gagal menjalankan search: {exc}[/red]")



def _handle_browser() -> None:
    console.print("\n[bold cyan]--- Browser Management ---[/bold cyan]")
    from shopee_cli.commands.browser import show_browser_status
    show_browser_status()


from dataclasses import dataclass
import json
import os


@dataclass
class ChromeProfileInfo:
    folder: str
    name: str
    email: str
    full_name: str


def _find_chrome_profiles_info() -> list[ChromeProfileInfo]:
    if sys.platform != "win32":
        return [ChromeProfileInfo(folder="Default", name="Default", email="", full_name="")]

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    user_data_dir = os.path.join(local_app_data, "Google", "Chrome", "User Data")
    local_state_path = os.path.join(user_data_dir, "Local State")

    cache_info = {}
    if os.path.exists(local_state_path):
        try:
            with open(local_state_path, encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                cache_info = data.get("profile", {}).get("info_cache", {})
        except Exception:
            pass

    profiles: list[ChromeProfileInfo] = []
    if os.path.exists(user_data_dir):
        try:
            for entry in os.listdir(user_data_dir):
                if entry == "Default" or entry.startswith("Profile "):
                    prof_data = cache_info.get(entry, {})
                    display_name = prof_data.get("name") or entry
                    email = prof_data.get("user_name") or ""
                    full_name = prof_data.get("gaia_name") or ""
                    profiles.append(
                        ChromeProfileInfo(
                            folder=entry,
                            name=display_name,
                            email=email,
                            full_name=full_name,
                        )
                    )
        except Exception:
            pass

    if not profiles:
        return [ChromeProfileInfo(folder="Default", name="Default", email="", full_name="")]

    def sort_key(p: ChromeProfileInfo) -> tuple[int, int | str]:
        if p.folder == "Default":
            return (0, 0)
        parts = p.folder.split()
        if len(parts) > 1 and parts[1].isdigit():
            return (1, int(parts[1]))
        return (1, p.folder)

    return sorted(profiles, key=sort_key)


def _handle_launch_chrome() -> None:
    console.print("\n[bold cyan]--- Launch Chrome Debugger ---[/bold cyan]")
    profiles = _find_chrome_profiles_info()

    table = Table(title="Profil Google Chrome Terdeteksi")
    table.add_column("No", style="cyan", width=4)
    table.add_column("Folder", style="dim", width=12)
    table.add_column("Nama Profil Chrome", style="bold white")
    table.add_column("Email Google", style="bold green")

    for idx, prof in enumerate(profiles, start=1):
        name_str = prof.name
        if prof.full_name and prof.full_name != prof.name:
            name_str = f"{prof.name} ({prof.full_name})"
        table.add_row(str(idx), prof.folder, name_str, prof.email or "-")

    console.print(table)

    choice = Prompt.ask(
        f"Pilih nomor profil Chrome (1-{len(profiles)})",
        choices=[str(i) for i in range(1, len(profiles) + 1)],
        default="1",
    )
    selected_info = profiles[int(choice) - 1]
    selected_profile = selected_info.folder

    if sys.platform == "win32":
        try:
            subprocess.Popen(["launch_chrome_debug.bat", selected_profile], shell=True)
            console.print(
                f"[green]Membuka Chrome dengan profil '[bold]{selected_info.name}[/bold]' ({selected_info.email or selected_profile}) di port 9222...[/green]"
            )
        except Exception as exc:
            console.print(f"[red]Gagal menjalankan script: {exc}[/red]")
    else:
        console.print("Jalankan Chrome manual dengan perintah:")
        console.print(
            f"[yellow]google-chrome --remote-debugging-port=9222 --profile-directory='{selected_profile}'[/yellow]"
        )


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
