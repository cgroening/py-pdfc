import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from pdfc.cli.compress_parameters import CompressRequest
from pdfc.cli.output import (
    print_info, print_success, print_warning, print_error, clear_lines
)
from pdfc.cli.input import InputView
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression_service import CompressionService


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
        self._print_compression_settings(self._compress_request.compression_settings)
        self._process_pdf_files()

    def _read_compression_settings_via_interactive_mode(self) -> None:
        """Collects CompressionSettings interactively via prompts."""
        if not self._compress_request.interactive_mode:
            return

        print_info('Starting interactive mode…\n')
        prompts = 0
        try:
            mode = self._input.prompt_mode();  prompts += 1  # 'bw' | 'gray' | 'color'
            dpi  = self._input.prompt_dpi();   prompts += 1

            tiff_ccitt       = False
            jpeg_quality     = None
            png_compression  = None

            if mode == 'bw':
                tiff_ccitt = self._input.prompt_tiff_ccitt(); prompts += 1

            if not tiff_ccitt:
                fmt = self._input.prompt_image_format(); prompts += 1  # 'jpeg' | 'png'
                if fmt == 'jpeg':
                    jpeg_quality    = self._input.prompt_jpeg_quality();    prompts += 1
                else:
                    png_compression = self._input.prompt_png_compression(); prompts += 1

            bw_threshold = None
            if mode == 'bw':
                bw_threshold = self._input.prompt_bw_threshold(); prompts += 1

            sharpen      = self._input.prompt_sharpen();      prompts += 1
            contrast     = self._input.prompt_contrast();     prompts += 1
            unsharp_mask = self._input.prompt_unsharp_mask(); prompts += 1

        except KeyboardInterrupt:
            print_info('\nInteractive mode cancelled.')
            sys.exit(0)
        except Exception as e:
            print_error(f'An error occurred: {e}')
            sys.exit(1)

        # Remove all prompt lines from the console before printing the final settings.
        # 2 lines for the header (info message + blank line), 1 per completed prompt
        clear_lines(2 + prompts)
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
        try:
            pdf_files = self._service.get_pdf_files(self._compress_request.input_path)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        if not pdf_files:
            print_error('No PDF files found.')
            sys.exit(1)

        self._pdf_files = pdf_files

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

    @staticmethod
    def _print_compression_settings(settings: CompressionSettings) -> None:
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

        settings_dict = settings.to_dict()
        names = list(settings_dict.keys())
        for name in names[:5]:
            left_table.add_row(name, settings_dict[name])
        for name in names[5:]:
            right_table.add_row(name, settings_dict[name])

        main_table.add_row(left_table, right_table)
        console.print()
        console.print(main_table)

    def _process_pdf_files(self):
        """
        Loops through all PDF files, compressing them one by one and
        printing results.
        """
        pdf_files = self._pdf_files
        for pdf_file_path in pdf_files:
            output_path = self._service.get_compress_output_path(
                pdf_file_path,
                self._compress_request.output_path
            )
            self._print_paths(
                source=pdf_file_path,
                target=output_path,
                target_is_generated=\
                    self._compress_request.input_path_is_directory()
            )
            try:
                self._service.compress_file(
                    pdf_file_path,
                    output_path,
                    self._compress_request.compression_settings
                )
                original_size_kb = pdf_file_path.stat().st_size / 1024
                compressed_size_kb = output_path.stat().st_size / 1024

                if original_size_kb:
                    savings = (1 - compressed_size_kb / original_size_kb) * 100
                else:
                    savings = 0.0
                msg = f'{output_path.name}  ({compressed_size_kb:.1f} KB, {savings:.1f}% savings)'
                print_success(msg)
            except Exception as e:
                print_error(f'{pdf_file_path.name}: {e}')

    @staticmethod
    def _print_paths(
        source: Path, target: Path, target_is_generated: bool = False
    ) -> None:
        """
        Prints source and target paths in a formatted table.

        Example
        -------
        ┌─────────┬─────────────────────────────────────────────────┐
        │ Source: │ /Users/cgroening/Downloads/input.pdf            │
        ├─────────┼─────────────────────────────────────────────────┤
        │ Target: │ /Users/cgroening/Downloads/input-compressed.pdf │
        │         │ (auto-generated)                                │
        └─────────┴─────────────────────────────────────────────────┘
        """
        target_str = str(target)
        if target_is_generated:
            target_str += '\n[yellow](auto-generated)[/yellow]'

        table = Table(show_header=False, show_lines=True)
        table.add_column('Label', style='bold magenta', no_wrap=True)
        table.add_column('Path')

        table.add_row('Source:', str(source))
        table.add_row('Target:', target_str)
        console.print(table)

