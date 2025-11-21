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
        self.console = Console()

    def show_result(self, person: CompressionSettings, verbose: bool = False):
        """
        Displays the person data.

        Parameters
        ----------
        person : Person
            The person data to display
        verbose : bool
            If True, show detailed table. If False, show compact format.
        """
        if verbose:
            self._show_verbose(person)
        else:
            self._show_compact(person)

    def _show_verbose(self, person: CompressionSettings):
        """Shows detailed table format."""
        table = Table(title='Person Information', show_header=True,
                     header_style='bold magenta')
        table.add_column('Field', style='cyan', width=12)
        table.add_column('Value', style='green')

        table.add_row('Name', person.name)
        table.add_row('Age', str(person.age) if person.age else 'N/A')
        table.add_row('Cars', ', '.join(person.cars) if person.cars else 'N/A')

        self.console.print(table)

    def _show_compact(self, person: CompressionSettings):
        """Shows compact format."""
        cars_str = ', '.join(person.cars) if person.cars else 'None'
        output = f'{person.name}; {person.age}; {cars_str}'
        self.console.print(Panel(output, title='Result', border_style='blue'))

    def show_error(self, message: str):
        """
        Displays an error message.

        Parameters
        ----------
        message : str
            The error message to display
        """
        self.console.print(f'[bold red]Error:[/bold red] {message}')

    def show_info(self, message: str):
        """
        Displays an info message.

        Parameters
        ----------
        message : str
            The info message to display
        """
        self.console.print(f'[bold blue]Info:[/bold blue] {message}')
