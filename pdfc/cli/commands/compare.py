"""
Compare command: runs multiple compression configurations and saves results
in a folder named after the input PDF for easy side-by-side comparison.
"""
import sys
from pathlib import Path
from pdfc.cli.output import OutputView
from pdfc.services.compression_service import CompressionService


class CompareCommand:
    """
    CLI command for batch-comparing compression configurations.

    For each input PDF a subdirectory is created (named after the PDF stem)
    and every configuration variant is written as a separate PDF into it.
    Contains no business logic.
    """

    _service: CompressionService
    _output: OutputView

    def __init__(self, service: CompressionService, output: OutputView) -> None:
        self._service = service
        self._output = output

    def run(self, input_path: Path, dpi: int, verbose: bool) -> None:
        # --- Find PDF files ---
        try:
            pdf_files = self._service.get_pdf_files(input_path)
        except ValueError as e:
            self._output.show_error(str(e))
            sys.exit(1)

        if not pdf_files:
            self._output.show_error('No PDF files found.')
            sys.exit(1)

        configs = self._service.get_compare_configs(dpi)
        total_files   = len(pdf_files)
        total_configs = len(configs)
        successful    = 0
        failed        = 0

        self._output.show_info(
            f'Found {total_files} PDF file(s) — '
            f'running {total_configs} configurations each.\n'
        )

        for pdf in pdf_files:
            out_dir = self._service.get_compare_output_dir(pdf)
            out_dir.mkdir(parents=True, exist_ok=True)

            self._output.show_compare_header(pdf, total_configs)
            input_size = pdf.stat().st_size

            for name, settings in configs:
                out_path = out_dir / f'{name}.pdf'
                try:
                    self._service.compress_file(pdf, out_path, settings)
                    self._output.show_compare_config_ok(
                        name, out_path.stat().st_size, input_size
                    )
                    successful += 1
                except Exception as e:
                    self._output.show_compare_config_error(name, str(e))
                    failed += 1

            self._output.cs.print()

        self._output.show_compare_summary(
            total_files, total_configs, successful, failed
        )
