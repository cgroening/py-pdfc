import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from pdfc.cli.compress_parameters import CompressRequest
from pdfc.cli.output import (
    print_info, print_warning, print_error, clear_lines,
    print_file_section_header, print_result_ok, print_result_error,
    print_summary
)
from pdfc.cli.commands.compress_input import InputView
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression import CompressionService


console = Console()


class CompressCommand:
    """
    CLI command for compressing one or more PDF files.

    Receives typed arguments from main.py, builds `CompressionSettings`,
    validates them and delegates to the service layer.
    """
    _service: CompressionService
    _input: InputView
    _compress_request: CompressRequest
    _pdf_files: list[Path]
    _successful: int = 0
    _failed: int = 0

    def __init__(
        self, service: CompressionService, input_view: InputView
    ) -> None:
        self._service = service
        self._input = input_view

    def run(self, compress_parameters: CompressRequest) -> None:
        self._compress_request = compress_parameters
        self._read_compression_settings_via_interactive_mode()
        self._validate_compression_settings()
        self._find_pdf_files_in_input_path()
        self._validate_output_path()
        self._print_source_target()
        self._print_compression_settings()
        self._process_pdf_files()
        self._print_summary()

    def _read_compression_settings_via_interactive_mode(self) -> None:
        """
        Collects the values for `CompressionSettings` interactively via prompts.
        """
        if not self._compress_request.interactive_mode:
            return

        input = self._input
        print_info('Starting interactive mode…')
        try:
            mode = input.prompt_mode()
            dpi  = input.prompt_dpi()

            tiff_ccitt       = False
            jpeg_quality     = None
            png_compression  = None

            if mode == 'bw':
                tiff_ccitt = input.prompt_tiff_ccitt()

            if not tiff_ccitt:
                fmt = input.prompt_image_format()
                if fmt == 'jpeg':
                    jpeg_quality    = input.prompt_jpeg_quality()
                else:
                    png_compression = input.prompt_png_compression()

            bw_threshold = None
            if mode == 'bw':
                bw_threshold = input.prompt_bw_threshold()

            sharpen      = input.prompt_sharpen()
            contrast     = input.prompt_contrast()
            unsharp_mask = input.prompt_unsharp_mask()

        except KeyboardInterrupt:
            print_info('Interactive mode cancelled.')
            sys.exit(0)
        except Exception as e:
            print_error(f'An error occurred: {e}')
            sys.exit(1)

        # Remove all prompt lines from the console before printing the final
        # settings: 6 lines for the header (info message + blank line) and
        # 1 per completed prompt
        clear_lines(6 + input.number_of_executed_prompts)
        self._compress_request.compression_settings = CompressionSettings(
            _mode=mode,
            _dpi=dpi,
            _jpeg_quality=jpeg_quality,
            _png_compression=png_compression,
            _bw_threshold=bw_threshold,
            _sharpen=sharpen,
            _contrast=contrast,
            _unsharp_mask=unsharp_mask,
            _tiff_ccitt=tiff_ccitt,
        )

    def _validate_compression_settings(self):
        try:
            self._service.validate(self._compress_request.compression_settings)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

    def _find_pdf_files_in_input_path(self) -> None:
        """
        Finds all PDF files in the input path and filters out already compressed
        files if the input is a directory and the no-skip flag is not set.
        """
        try:
            pdf_files = self._service.get_pdf_files(
                self._compress_request.input_path
            )
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        pdf_files = self._filter_already_compressed_files(pdf_files)

        if not pdf_files:
            print_error('No PDF files found.')
            sys.exit(1)

        self._pdf_files = pdf_files

    def _filter_already_compressed_files(self, pdf_files) -> list[Path]:
        """
        If the input path is a directory and the no-skip flag is not set, filter
        out files that have already been compressed (i.e. files whose name ends
        with `-compressed.pdf`) and print a warning for each skipped file.
        """
        if self._compress_request.input_path.is_dir() \
        and not self._compress_request.no_skip:
            filtered = []
            for f in pdf_files:
                if f.stem.endswith('-compressed'):
                    print_warning(f'Skipping already compressed file: {f.name}')
                else:
                    filtered.append(f)
            pdf_files = filtered
        return pdf_files

    def _validate_output_path(self):
        """
        Return a warning if an output path is provided for multiple input files
        because in that case the output path will be ignored and auto-generated
        for each file.
        """
        if self._compress_request.input_path.is_dir() \
        and self._compress_request.output_path is not None:
            print_warning(
                'Output path is ignored when the input is a directory.'
                'The output path will be auto-generated for each file in the '
                'same directory as the input file.'
            )
            self._compress_request.output_path = None

    def _print_compression_settings(self) -> None:
        """
        Prints the compression settings split into two side-by-side tables.

        Example
        -------
                       Compression Settings
        ┏━━━━━━━━━━━━━━┳━━━━━━━┓ ┏━━━━━━━━━━━━━━┳━━━━━━━┓
        ┃ Setting      ┃ Value ┃ ┃ Setting      ┃ Value ┃
        ┡━━━━━━━━━━━━━━╇━━━━━━━┩ ┡━━━━━━━━━━━━━━╇━━━━━━━┩
        │ Mode         │ B&W   │ │ BW Threshold │ 150   │
        │ DPI          │ 300   │ │ Sharpen      │ 0.0   │
        │ Format       │ JPEG  │ │ Contrast     │ 1.0   │
        │ JPEG Quality │ 20    │ │ Unsharp Mask │ No    │
        │ PNG Level    │ -     │ │ TIFF CCITT   │ No    │
        └──────────────┴───────┘ └──────────────┴───────┘
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

        settings_dict = self._compress_request.compression_settings.to_dict()
        names = list(settings_dict.keys())
        for name in names[:5]:
            left_table.add_row(name, settings_dict[name])
        for name in names[5:]:
            right_table.add_row(name, settings_dict[name])

        main_table.add_row(left_table, right_table)
        console.print()
        console.print(main_table)

    def _process_pdf_files(self) -> None:
        """Loops through all PDF files and compresses them one by one."""
        for pdf in self._pdf_files:
            output_path = self._service.get_output_path(
                pdf, self._compress_request.output_path
            )
            self._compress_single_file(pdf, output_path)

    def _print_source_target(self) -> None:
        req = self._compress_request
        console.print(f'\n  [dim]Source:[/dim] {req.input_path}')
        if req.input_path_is_directory():
            console.print(
                '  [dim]Target:[/dim] [dim](auto-generated per file)[/dim]'
            )
        elif req.output_path is not None:
            console.print(f'  [dim]Target:[/dim] {req.output_path}')
        else:
            target = self._service.get_output_path(self._pdf_files[0], None)
            console.print(f'  [dim]Target:[/dim] {target}')

    def _compress_single_file(
        self, pdf_file_path: Path, output_path: Path
    ) -> None:
        """Compresses a single PDF file and prints the result."""
        print_file_section_header(pdf_file_path, pdf_file_path.stat().st_size)
        try:
            self._service.compress_file(
                pdf_file_path, output_path,
                self._compress_request.compression_settings,
            )
            original_kb = pdf_file_path.stat().st_size / 1024
            compressed_kb = output_path.stat().st_size / 1024
            if original_kb == 0:
                savings = 0.0
            else:
                savings = (1 - compressed_kb / original_kb) * 100
            print_result_ok(output_path.name, compressed_kb, savings)
            self._successful += 1
        except Exception as e:
            print_result_error(pdf_file_path.name, str(e))
            self._failed += 1

    def _print_summary(self) -> None:
        items = [('Compressed:', f'[green]{self._successful}[/green]')]
        if self._failed:
            items.append(('Failed:', f'[red]{self._failed}[/red]'))
        print_summary(items)

