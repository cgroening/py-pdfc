"""
Output view using Rich for formatted display.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from models.compression_settings_model import CompressionSettings


class OutputView:
    """Handles all output formatting using Rich."""

    def __init__(self):
        """Initializes the console."""
        self.cs = Console()

    def show_info(self, message: str):
        self.cs.print(f'[bold blue]Info:[/bold blue] {message}')

    def show_success(self, message: str):
        self.cs.print(f'[bold green]Success:[/bold green] {message}')

    def show_warning(self, message: str):
        self.cs.print(f'[bold yellow]Warning:[/bold yellow] {message}')

    def show_error(self, message: str):
        self.cs.print(f'[bold red]Error:[/bold red] {message}')

    def print_input_values(self, settings: CompressionSettings):
        table = Table(title='Compression Settings', show_header=True, header_style='bold magenta')
        table.add_column('Setting', style='cyan', no_wrap=True)
        table.add_column('Value', style='green')

        for setting, value in settings.to_dict().items():
            table.add_row(setting, str(value) if value is not None else 'None')

        self.cs.print(table)
