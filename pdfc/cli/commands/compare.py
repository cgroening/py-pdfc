import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from pdfc.cli.output import print_error, print_info
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression import CompressionService


console = Console()


class CompareCommand:
    """
    CLI command for batch-comparing compression configurations.

    For each input PDF a subdirectory is created (named after the PDF stem)
    and every configuration variant is written as a separate PDF into it.

    Attributes
    ----------
    _service : CompressionService
        The service responsible for all compression logic and file handling.
    _pdf_files : list[Path]
        List of PDF files found in the input directory.
    _configs : list[tuple[str, CompressionSettings]]
        List of compression configurations to compare, each with a name
        and settings.
    _total_files : int
        Total number of PDF files found.
    _total_configs : int
        Total number of compression configurations to run.
    _successful : int
        Counter for successful compressions.
    _failed : int
        Counter for failed compressions.
    """
    _service: CompressionService
    _pdf_files: list[Path]
    _configs: list[tuple[str, CompressionSettings]]
    _total_files: int
    _total_configs: int
    _successful: int = 0
    _failed: int = 0


    def __init__(self, service: CompressionService) -> None:
        self._service = service

    def run(self, input_path: Path, dpi: int) -> None:
        self._find_pdf_files_in_path(input_path)
        self._get_compare_configs(dpi)
        self._print_number_of_found_pdf_files_and_configs()
        self._process_pdf_files()
        self._show_compare_summary()

    def _find_pdf_files_in_path(self, input_path: Path) -> None:
        try:
            pdf_files = self._service.get_pdf_files(input_path)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        if not pdf_files:
            print_error('No PDF files found.')
            sys.exit(1)

        self._pdf_files = pdf_files
        self._total_files = len(pdf_files)

    def _get_compare_configs(self, dpi: int) -> None:
        try:
            configs = self._service.get_compare_configs(dpi)
        except (FileNotFoundError, ValueError) as e:
            print_error(str(e))
            sys.exit(1)

        self._configs = configs
        self._total_configs = len(configs)

    def _print_number_of_found_pdf_files_and_configs(self) -> None:
        print_info(
            f'Found {self._total_files} PDF file(s) — '
            f'running {self._total_configs} configurations each.'
        )

    def _process_pdf_files(self):
        for pdf_file_path in self._pdf_files:
            out_dir = self._service.get_compare_output_dir(pdf_file_path)
            out_dir.mkdir(parents=True, exist_ok=True)

            self._print_compare_header(pdf_file_path, self._total_configs)
            input_size = pdf_file_path.stat().st_size

            self._run_configs_for_file(pdf_file_path, input_size, out_dir)

            console.print()

    def _run_configs_for_file(
        self, pdf_file_path: Path, input_size: int, out_dir: Path
    ) -> None:
        for name, compression_settings in self._configs:
            output_path = out_dir / f'{name}.pdf'
            try:
                self._service.compress_file(
                    pdf_file_path, output_path, compression_settings
                )
                self._print_compare_config_ok(
                    name, output_path.stat().st_size, input_size
                )
                self._successful += 1
            except Exception as e:
                self._print_compare_config_error(name, str(e))
                self._failed += 1

    @staticmethod
    def _print_compare_header(pdf_path: Path, total_configs: int) -> None:
        """Prints the header for a single PDF being compared."""
        console.rule(f'[bold cyan]{pdf_path.name}[/bold cyan]')
        console.print(
            f'[dim]Running {total_configs} configurations …[/dim]\n'
        )

    @staticmethod
    def _print_compare_config_ok(
        name: str, output_size: int, input_size: int
    ) -> None:
        """Prints a success line for one compare configuration."""
        kb = output_size / 1024
        savings = (1 - output_size / input_size) * 100 if input_size else 0
        console.print(
            f'  [green]✓[/green] [cyan]{name:<45}[/cyan] '
            f'[green]{kb:>8.1f} KB[/green]  '
            f'[dim]({savings:.1f}% savings)[/dim]'
        )

    @staticmethod
    def _print_compare_config_error(name: str, error: str) -> None:
        """Prints an error line for one compare configuration."""
        console.print(
            f'  [red]✗[/red] [cyan]{name:<45}[/cyan] '
            f'[red]{error}[/red]'
        )

    def _show_compare_summary(self) -> None:
        """
        Prints the overall summary table after all files and configurations
        have been processed. Shows total files, total configurations and counts
        of successful and failed compressions.
        """
        console.rule()
        table = Table(show_header=False, box=None)
        table.add_column('', style='dim')
        table.add_column('', style='bold')
        table.add_row('PDF files processed:', str(self._total_files))
        table.add_row('Configurations per file:', str(self._total_configs))
        table.add_row('Successful:', f'[green]{self._successful}[/green]')
        if self._failed:
            table.add_row('Failed:', f'[red]{self._failed}[/red]')
        console.print(table)

