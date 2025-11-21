"""
Output view using Rich for formatted display.
"""
import math
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.columns import Columns
from rich.panel import Panel
from rich.align import Align
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
        self.print_compression_settings(settings)
        self.print_paths('/this/is/the/source.pdf', '/this/is/the/target.pdf')

    def print_compression_settings(self, settings: CompressionSettings):
        """
        Prints the compression settings in a formatted table.

        For a better use of space, the settings are split into two columns.
        This is achieved by creating two separate tables and placing them side
        by side in a parent table. The layout looks like this (the dashed lines
        represent the borders of the parent table which are not actually drawn):

        ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
         ┌────────────┬──────────┐ │ ┌────────────┬──────────┐│
        ││ Setting    │ Value    │ │ │ Setting    │ Value    │
         ├────────────┼──────────┤ │ ├────────────┼──────────┤│
        ││ Setting 1  │ Value 1  │ │ │ Setting 3  │ Value 3  │
         │ Setting 2  │ Value 2  │ │ │ Setting 4  │ Value 4  ││
        ││ ...        │ ...      │ │ │ ...        │ ...      │
         └────────────┴──────────┘ │ └────────────┴──────────┘│
        └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─└ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

        Parameters
        ----------
        settings : CompressionSettings
            The compression settings to display.
        """
        # Main table with two columns
        main_table = Table(
            title='Compression Settings',
            show_header=False, box=None, padding=(0, 1, 0, 0)
        )
        main_table.add_column('')
        main_table.add_column('')

        # Left table
        left_table = Table(show_header=True, header_style='bold magenta')
        left_table.add_column('Setting', style='cyan', no_wrap=True)
        left_table.add_column('Value', style='green')

        # Right table
        right_table = Table(show_header=True, header_style='bold magenta')
        right_table.add_column('Setting', style='cyan', no_wrap=True)
        right_table.add_column('Value', style='green')

        # Get settings as dictionary (key: setting name, value: setting value)
        # Pop all values from settings_dict with the value "-"
        settings_dict = {k: v for k, v in settings.to_dict().items() if v != "-"}
        setting_names = list(settings_dict.keys())
        offset = int(math.ceil(len(settings_dict) / 2))

        # Fill both tables
        for i in range(offset):
            # Left table
            setting = setting_names[i]
            value = str(settings_dict[setting])
            left_table.add_row(setting, value)

            # Right table
            if i + offset < len(setting_names):  # Check index bounds
                setting = setting_names[i + offset]
                value = str(settings_dict[setting])
                right_table.add_row(setting, value)

        # Add both tables to the main table
        main_table.add_row(left_table, right_table)
        self.cs.print(main_table)

    def print_paths(self, source: str, target: str | None = None):
        pass


