"""
Output view using Rich for formatted display.
"""
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from pdfc.domain.models import CompressionSettings


class OutputView:
    """Handles all output formatting using Rich."""

    cs: Console

    def __init__(self):
        self.cs = Console()

    # ------------------------------------------------------------------
    # Cursor helpers
    # ------------------------------------------------------------------

    def clear_lines(self, count: int) -> None:
        """Move cursor up `count` lines and clear everything below."""
        sys.stdout.write(f'\033[{count}A\033[0J')
        sys.stdout.flush()

    # ------------------------------------------------------------------
    # Generic messages
    # ------------------------------------------------------------------

    def show_info(self, message: str) -> None:
        self.cs.print(f'[bold blue]Info:[/bold blue] {message}')

    def show_success(self, message: str) -> None:
        self.cs.print(f'[bold green]Success:[/bold green] {message}')

    def show_warning(self, message: str) -> None:
        self.cs.print(f'[bold yellow]Warning:[/bold yellow] {message}')

    def show_error(self, message: str) -> None:
        self.cs.print(f'[bold red]Error:[/bold red] {message}')

    # ------------------------------------------------------------------
    # Compression settings display
    # ------------------------------------------------------------------

    def print_compression_settings(self, settings: CompressionSettings) -> None:
        """
        Prints the compression settings split into two side-by-side tables.
        """
        main_table = Table(
            title='Compression Settings',
            show_header=False, box=None, padding=(0, 1, 0, 0),
        )
        main_table.add_column('')
        main_table.add_column('')

        left_table = Table(show_header=True, header_style='bold magenta')
        left_table.add_column('Setting', style='cyan', no_wrap=True)
        left_table.add_column('Value', style='green')

        right_table = Table(show_header=True, header_style='bold magenta')
        right_table.add_column('Setting', style='cyan', no_wrap=True)
        right_table.add_column('Value', style='green')

        settings_dict = settings.to_dict()
        names = list(settings_dict.keys())
        for name in names[:5]:
            left_table.add_row(name, settings_dict[name])
        for name in names[5:]:
            right_table.add_row(name, settings_dict[name])

        main_table.add_row(left_table, right_table)
        self.cs.print()
        self.cs.print(main_table)

    def print_paths(self, source: Path, target: Path, target_auto: bool = False) -> None:
        """Prints source and target paths in a formatted table."""
        target_str = str(target)
        if target_auto:
            target_str += '\n[yellow](auto-generated)[/yellow]'

        table = Table(show_header=False, show_lines=True)
        table.add_column('Label', style='bold magenta', no_wrap=True)
        table.add_column('Path')

        table.add_row('Source:', str(source))
        table.add_row('Target:', target_str)
        self.cs.print(table)

    # ------------------------------------------------------------------
    # Compare output
    # ------------------------------------------------------------------

    def show_compare_header(self, pdf_path: Path, total_configs: int) -> None:
        """Prints the header for a single PDF being compared."""
        self.cs.rule(f'[bold cyan]{pdf_path.name}[/bold cyan]')
        self.cs.print(
            f'[dim]Running {total_configs} configurations …[/dim]\n'
        )

    def show_compare_config_ok(
        self,
        name: str,
        output_size: int,
        input_size: int,
    ) -> None:
        """Prints a success line for one compare configuration."""
        kb = output_size / 1024
        savings = (1 - output_size / input_size) * 100 if input_size else 0
        self.cs.print(
            f'  [green]✓[/green] [cyan]{name:<45}[/cyan] '
            f'[green]{kb:>8.1f} KB[/green]  '
            f'[dim]({savings:.1f}% savings)[/dim]'
        )

    def show_compare_config_error(self, name: str, error: str) -> None:
        """Prints an error line for one compare configuration."""
        self.cs.print(
            f'  [red]✗[/red] [cyan]{name:<45}[/cyan] '
            f'[red]{error}[/red]'
        )

    def show_compare_summary(
        self,
        total_files: int,
        total_configs: int,
        successful: int,
        failed: int,
    ) -> None:
        """Prints the overall summary table."""
        self.cs.rule()
        table = Table(show_header=False, box=None)
        table.add_column('', style='dim')
        table.add_column('', style='bold')
        table.add_row('PDF files processed:', str(total_files))
        table.add_row('Configurations per file:', str(total_configs))
        table.add_row('Successful:', f'[green]{successful}[/green]')
        if failed:
            table.add_row('Failed:', f'[red]{failed}[/red]')
        self.cs.print(table)
