"""
Compress command: validates settings, finds PDF files and compresses them.
"""
import sys
from pathlib import Path
from typing import Optional
from pdfc.domain.models import CompressionSettings
from pdfc.cli.output import OutputView
from pdfc.cli.input import InputView
from pdfc.services.compression_service import CompressionService


class CompressCommand:
    """
    CLI command for compressing one or more PDF files.

    Receives typed arguments from main.py, builds CompressionSettings,
    validates them and delegates to the service layer. Contains no
    business logic.
    """

    _service: CompressionService
    _output: OutputView
    _input: InputView

    def __init__(
        self,
        service: CompressionService,
        output: OutputView,
        input_view: InputView,
    ) -> None:
        self._service = service
        self._output = output
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
        tiff_ccitt: bool,
        verbose: bool,
    ) -> None:
        # --- Guard: both JPEG quality and PNG level given ---
        if jpeg_quality is not None and png_compression_level is not None:
            self._output.show_error(
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
            self._output.show_error(f'Failed to build settings: {e}')
            sys.exit(1)

        # --- Validate ---
        try:
            self._service.validate(settings)
        except ValueError as e:
            self._output.show_error(str(e))
            sys.exit(1)

        # --- Find PDF files ---
        try:
            pdf_files = self._service.get_pdf_files(input_path)
        except ValueError as e:
            self._output.show_error(str(e))
            sys.exit(1)

        if not pdf_files:
            self._output.show_error('No PDF files found.')
            sys.exit(1)

        # output_path only makes sense for a single file
        if input_path.is_dir() and output_path is not None:
            self._output.show_warning(
                'Output path is ignored when the input is a directory.'
            )
            output_path = None

        # --- Print settings ---
        self._output.print_compression_settings(settings)

        # --- Compress each file ---
        for pdf in pdf_files:
            out = self._service.get_compress_output_path(
                pdf,
                output_path if len(pdf_files) == 1 else None,
            )
            auto = output_path is None or len(pdf_files) > 1
            self._output.print_paths(pdf, out, target_auto=auto)
            try:
                self._service.compress_file(pdf, out, settings)
                size_kb = out.stat().st_size / 1024
                orig_kb = pdf.stat().st_size / 1024
                savings = (1 - size_kb / orig_kb) * 100 if orig_kb else 0
                msg = f'{out.name}  ({size_kb:.1f} KB, {savings:.1f}% savings)'
                self._output.show_success(msg)
            except Exception as e:
                self._output.show_error(f'{pdf.name}: {e}')

    # ------------------------------------------------------------------

    def _run_interactive_mode(self) -> CompressionSettings:
        """Collects CompressionSettings interactively via prompts."""
        self._output.show_info('Starting interactive mode…\n')
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
            self._output.show_info('\nInteractive mode cancelled.')
            sys.exit(0)
        except Exception as e:
            self._output.show_error(f'An error occurred: {e}')
            sys.exit(1)

        # Remove all prompt lines from the console before printing the final settings.
        # 2 lines for the header (info message + blank line), 1 per completed prompt
        self._output.clear_lines(2 + prompts)
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
