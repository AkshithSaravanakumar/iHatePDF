"""Interactive Command Line Interface for iHatePDF."""

import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt

from ihatepdf import __version__
from ihatepdf.utils import (
    format_size,
    validate_file_path,
)
from ihatepdf.core.pdf_compressor import compress_pdf, get_pdf_info
from ihatepdf.core.pdf_splitter import split_pdf_in_half
from ihatepdf.core.image_compressor import (
    compress_image,
    get_image_info,
    CompressionLevel,
)

console = Console()

BANNER_ART = r"""
██╗██╗  ██╗ █████╗ ████████╗███████╗
██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝
██║███████║███████║   ██║   █████╗
██║██╔══██║██╔══██║   ██║   ██╔══╝
██║██║  ██║██║  ██║   ██║   ███████╗
╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝  ᴘᴅꜰ
"""


def display_banner() -> None:
    """Render the ASCII banner, tagline, and version."""
    banner_text = Text(BANNER_ART.strip("\n"), style="bold cyan")
    console.print(banner_text)
    
    subtitle = Text.assemble(
        ("You Know Who ", "italic yellow"),
        (f"(v{__version__})", "bold green")
    )
    console.print(subtitle)
    console.print()


def display_menu() -> str:
    """Display the main interactive menu and get user selection."""
    console.print("[bold white]Choose an operation:[/bold white]")
    console.print("  [bold cyan]1.[/bold cyan] Compress PDF")
    console.print("  [bold cyan]2.[/bold cyan] Split PDF in half")
    console.print("  [bold cyan]3.[/bold cyan] Compress Image")
    console.print("  [bold cyan]4.[/bold cyan] Exit")
    console.print()
    
    choice = Prompt.ask(
        "[bold green]Select an option[/bold green]",
        choices=["1", "2", "3", "4"],
        default="1"
    )
    return choice


def handle_compress_pdf() -> None:
    """Handle the interactive Compress PDF workflow."""
    console.print("\n[bold cyan]=== 1. Compress PDF ===[/bold cyan]")
    path_input = Prompt.ask("[bold]Enter PDF file path[/bold] (or 'q' to return to menu)")
    if path_input.strip().lower() in ("q", "quit", "exit"):
        return

    try:
        pdf_path = validate_file_path(path_input, (".pdf",))
        orig_size, num_pages = get_pdf_info(pdf_path)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}\n")
        return

    # Display initial file info
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="bold")
    info_table.add_column("Value", style="cyan")
    info_table.add_row("File name:", pdf_path.name)
    info_table.add_row("Original file size:", format_size(orig_size))
    info_table.add_row("Number of pages:", str(num_pages))
    
    console.print("\n[bold]Input File Details:[/bold]")
    console.print(info_table)
    console.print()

    with console.status("[bold green]Compressing PDF...[/bold green]", spinner="dots"):
        try:
            result = compress_pdf(pdf_path)
        except Exception as e:
            console.print(f"[bold red]Compression failed:[/bold red] {e}\n")
            return

    # Display completion results
    result_table = Table(title="[bold green]Compression Complete[/bold green]", box=None, padding=(0, 2))
    result_table.add_column("Metric", style="bold")
    result_table.add_column("Value", style="white")
    result_table.add_row("Original size:", format_size(result.original_size))
    result_table.add_row("Compressed size:", format_size(result.compressed_size))
    result_table.add_row("Space saved:", format_size(result.space_saved))
    
    reduction_color = "green" if result.reduction_percentage > 0 else "yellow"
    result_table.add_row("Reduction:", f"[{reduction_color}]{result.reduction_percentage:.1f}%[/{reduction_color}]")
    result_table.add_row("Output filename:", str(result.output_path.name))
    result_table.add_row("Output path:", str(result.output_path))

    console.print(Panel(result_table, border_style="green", expand=False))
    console.print()


def handle_split_pdf() -> None:
    """Handle the interactive Split PDF in half workflow."""
    console.print("\n[bold cyan]=== 2. Split PDF in Half ===[/bold cyan]")
    path_input = Prompt.ask("[bold]Enter PDF file path[/bold] (or 'q' to return to menu)")
    if path_input.strip().lower() in ("q", "quit", "exit"):
        return

    try:
        pdf_path = validate_file_path(path_input, (".pdf",))
        with console.status("[bold green]Analyzing and splitting PDF...[/bold green]", spinner="dots"):
            result = split_pdf_in_half(pdf_path)
    except Exception as e:
        console.print(f"[bold red]Split failed:[/bold red] {e}\n")
        return

    # Display split results
    split_table = Table(title=f"[bold green]Split Complete ({result.total_pages} Total Pages)[/bold green]", box=None, padding=(0, 2))
    split_table.add_column("Part", style="bold cyan")
    split_table.add_column("Pages", style="white")
    split_table.add_column("Output Filename", style="bold white")
    
    p1_start, p1_end = result.part1_range
    p2_start, p2_end = result.part2_range
    
    split_table.add_row(
        "Part 1",
        f"Pages {p1_start}-{p1_end} ({result.part1_count} pages)",
        str(result.part1_path.name)
    )
    split_table.add_row(
        "Part 2",
        f"Pages {p2_start}-{p2_end} ({result.part2_count} pages)",
        str(result.part2_path.name)
    )

    console.print(Panel(split_table, border_style="green", expand=False))
    console.print(f"[dim]Saved to: {result.part1_path.parent}[/dim]\n")


def handle_compress_image() -> None:
    """Handle the interactive Compress Image workflow."""
    console.print("\n[bold cyan]=== 3. Compress Image ===[/bold cyan]")
    allowed_exts = (".jpg", ".jpeg", ".png", ".webp")
    path_input = Prompt.ask("[bold]Enter image file path (JPG, PNG, WEBP)[/bold] (or 'q' to return to menu)")
    if path_input.strip().lower() in ("q", "quit", "exit"):
        return

    try:
        img_path = validate_file_path(path_input, allowed_exts)
        info = get_image_info(img_path)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}\n")
        return

    # Display initial image details
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="bold")
    info_table.add_column("Value", style="cyan")
    info_table.add_row("File name:", img_path.name)
    info_table.add_row("Format:", info.format)
    info_table.add_row("Original dimensions:", f"{info.dimensions[0]} x {info.dimensions[1]} px")
    info_table.add_row("Original file size:", format_size(info.file_size))

    console.print("\n[bold]Image Details:[/bold]")
    console.print(info_table)
    console.print()

    console.print("[bold white]Select Compression Level:[/bold white]")
    console.print("  [bold cyan]1.[/bold cyan] Low compression / high quality")
    console.print("  [bold cyan]2.[/bold cyan] Medium compression")
    console.print("  [bold cyan]3.[/bold cyan] High compression / smaller file")
    console.print()

    level_choice = IntPrompt.ask(
        "[bold green]Choose level[/bold green]",
        choices=["1", "2", "3"],
        default=2
    )
    level_enum = CompressionLevel(int(level_choice))

    with console.status("[bold green]Compressing image...[/bold green]", spinner="dots"):
        try:
            result = compress_image(img_path, level=level_enum)
        except Exception as e:
            console.print(f"[bold red]Image compression failed:[/bold red] {e}\n")
            return

    # Display completion results
    result_table = Table(title="[bold green]Image Compression Complete[/bold green]", box=None, padding=(0, 2))
    result_table.add_column("Metric", style="bold")
    result_table.add_column("Value", style="white")
    result_table.add_row("Original size:", format_size(result.original_size))
    result_table.add_row("Compressed size:", format_size(result.compressed_size))
    result_table.add_row("Space saved:", format_size(result.space_saved))
    
    reduction_color = "green" if result.reduction_percentage > 0 else "yellow"
    result_table.add_row("Reduction:", f"[{reduction_color}]{result.reduction_percentage:.1f}%[/{reduction_color}]")
    result_table.add_row("Output filename:", str(result.output_path.name))
    result_table.add_row("Output path:", str(result.output_path))

    console.print(Panel(result_table, border_style="green", expand=False))
    console.print()


def main() -> None:
    """Main CLI entrypoint loop."""
    try:
        display_banner()
        
        while True:
            choice = display_menu()
            
            if choice == "1":
                handle_compress_pdf()
            elif choice == "2":
                handle_split_pdf()
            elif choice == "3":
                handle_compress_image()
            elif choice == "4":
                console.print("[bold cyan]Goodbye! PDFs may be annoying, but you're all set.[/bold cyan]")
                sys.exit(0)
                
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold yellow]\nSession cancelled. Goodbye![/bold yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
