import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from pdfc.domain.models import CompressionSettings
from pdfc.cli.output import (
    print_info, print_success, print_warning, print_error, clear_lines
)
from pdfc.cli.input import InputView
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

    def __init__(
        self,
        service: CompressionService,
        input_view: InputView,
    ) -> None:
        self._service = service
        self._input = input_view

    def run(
        self,
        interactive: bool,
        input_path: Path,
        output_path: Optional[Path],
        mode: Optional[str],
        dpi: Optional[int],
        jpeg_quality: Optional[int],
        png_compression_level: Optional[int],
        threshold: Optional[int],
        sharpen: Optional[float],
        contrast: Optional[float],
        unsharp_mask: bool,
        tiff_ccitt: bool
    ) -> None:
        # --- Guard: both JPEG quality and PNG level given ---
        if jpeg_quality is not None and png_compression_level is not None:
            print_error(
                'Cannot use --jpeg-quality and --png-compression-level at the '
                'same time. Specify only one.'
            )
            sys.exit(1)

        # --- Build compression settings ---
        try:
            if interactive:
                settings = self._run_interactive_mode()
            else:
                settings = CompressionSettings(
                    _mode=mode,
                    _dpi=dpi,
                    _jpeg_quality=jpeg_quality,
                    _png_compression=png_compression_level,
                    _bw_threshold=threshold,
                    _sharpen=sharpen,
                    _contrast=contrast,
                    _unsharp_mask=unsharp_mask,
                    _tiff_ccitt=tiff_ccitt,
                )
        except Exception as e:
            print_error(f'Failed to build settings: {e}')
            sys.exit(1)

        # --- Validate ---
        try:
            self._service.validate(settings)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        # --- Find PDF files ---
        try:
            pdf_files = self._service.get_pdf_files(input_path)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        if not pdf_files:
            print_error('No PDF files found.')
            sys.exit(1)

        # output_path only makes sense for a single file
        if input_path.is_dir() and output_path is not None:
            print_warning(
                'Output path is ignored when the input is a directory.'
            )
            output_path = None

        # --- Print settings ---
        self._print_compression_settings(settings)

        # --- Compress each file ---
        for pdf in pdf_files:
            out = self._service.get_compress_output_path(
                pdf,
                output_path if len(pdf_files) == 1 else None,
            )
            auto = output_path is None or len(pdf_files) > 1
            self._print_paths(pdf, out, target_auto=auto)
            try:
                self._service.compress_file(pdf, out, settings)
                size_kb = out.stat().st_size / 1024
                orig_kb = pdf.stat().st_size / 1024
                savings = (1 - size_kb / orig_kb) * 100 if orig_kb else 0
                msg = f'{out.name}  ({size_kb:.1f} KB, {savings:.1f}% savings)'
                print_success(msg)
            except Exception as e:
                print_error(f'{pdf.name}: {e}')

    # ------------------------------------------------------------------

    def _run_interactive_mode(self) -> CompressionSettings:
        """Collects CompressionSettings interactively via prompts."""
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
        return CompressionSettings(
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

    @staticmethod
    def _print_compression_settings(settings: CompressionSettings) -> None:
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
        console.print()
        console.print(main_table)

    @staticmethod
    def _print_paths(source: Path, target: Path, target_auto: bool = False) -> None:
        """Prints source and target paths in a formatted table."""
        target_str = str(target)
        if target_auto:
            target_str += '\n[yellow](auto-generated)[/yellow]'

        table = Table(show_header=False, show_lines=True)
        table.add_column('Label', style='bold magenta', no_wrap=True)
        table.add_column('Path')

        table.add_row('Source:', str(source))
        table.add_row('Target:', target_str)
        console.print(table)
