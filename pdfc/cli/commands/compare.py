import sys
from pathlib import Path

from rich.console import Console
from pdfc.cli.output import (
    print_error, print_info,
    print_file_section_header, print_result_ok, print_result_error,
    print_summary, print_presets_table
)
from pdfc.cli.commands.pdf_file_filter import filter_already_compressed_files
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression import CompressionService


console = Console()


class CompareCommand:
    """
    CLI command for batch-comparing compression presets (configurations).

    For each input PDF a subdirectory is created (named after the PDF stem)
    and every configuration variant is written as a separate PDF into it.

    Attributes
    ----------
    _service : CompressionService
        The service responsible for all compression logic and file handling.
    _pdf_files : list[Path]
        List of PDF files found in the input directory.
    _presets : list[tuple[str, CompressionSettings]]
        List of compression presets to compare, each with a name and settings.
    _total_files : int
        Total number of PDF files found.
    _total_presets : int
        Total number of compression presets to run.
    _successful : int
        Counter for successful compressions.
    _failed : int
        Counter for failed compressions.
    """
    _service: CompressionService
    _pdf_files: list[Path]
    _presets: list[tuple[str, CompressionSettings]]
    _total_files: int
    _total_presets: int
    _successful: int = 0
    _failed: int = 0


    def __init__(self, service: CompressionService) -> None:
        self._service = service

    def run(self, input_path: Path, dpi: int) -> None:
        self._find_pdf_files_in_path(input_path)
        self._get_presets(dpi)
        self._print_number_of_found_pdf_files_and_presets()
        print_presets_table(self._presets, input_path=input_path)
        self._process_pdf_files()
        self._show_compare_summary()

    def _find_pdf_files_in_path(self, input_path: Path) -> None:
        try:
            pdf_files = self._service.get_pdf_files(input_path)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        if input_path.is_dir():
            pdf_files = filter_already_compressed_files(pdf_files)

        if not pdf_files:
            print_error('No PDF files found.')
            sys.exit(1)

        self._pdf_files = pdf_files
        self._total_files = len(pdf_files)

    def _get_presets(self, dpi: int) -> None:
        try:
            presets = self._service.get_presets(dpi)
        except (FileNotFoundError, ValueError) as e:
            print_error(str(e))
            sys.exit(1)

        self._presets = presets
        self._total_presets = len(presets)

    def _print_number_of_found_pdf_files_and_presets(self) -> None:
        print_info(
            f'Found {self._total_files} PDF file(s) - '
            f'running {self._total_presets} presets each.'
        )

    def _process_pdf_files(self):
        for pdf_file_path in self._pdf_files:
            out_dir = self._service.get_compare_output_dir(pdf_file_path)
            out_dir.mkdir(parents=True, exist_ok=True)

            print_file_section_header(
                pdf_file_path, pdf_file_path.stat().st_size
            )
            console.print(
                f'  [dim]Running {self._total_presets} presets …[/dim]\n'
            )
            input_size = pdf_file_path.stat().st_size

            self._run_presets_for_file(pdf_file_path, input_size, out_dir)

            console.print()

    def _run_presets_for_file(
        self, pdf_file_path: Path, input_size: int, out_dir: Path
    ) -> None:
        for name, compression_settings in self._presets:
            output_path = out_dir / f'{name}.pdf'
            try:
                self._service.compress_file(
                    pdf_file_path, output_path, compression_settings
                )
                output_kb = output_path.stat().st_size / 1024
                savings = (1 - output_path.stat().st_size / input_size) * 100 \
                    if input_size else 0
                print_result_ok(name, output_kb, savings)
                self._successful += 1
            except Exception as e:
                print_result_error(name, str(e))
                self._failed += 1

    def _show_compare_summary(self) -> None:
        """
        Prints the overall summary after all files and presets have been
        processed. Shows total files, total presets and counts of successful
        and failed compressions.
        """
        items = [
            ('PDF files processed:', str(self._total_files)),
            ('Presets per file:',    str(self._total_presets)),
            ('Successful:',          f'[green]{self._successful}[/green]'),
        ]
        if self._failed:
            items.append(('Failed:', f'[red]{self._failed}[/red]'))
        print_summary(items)

