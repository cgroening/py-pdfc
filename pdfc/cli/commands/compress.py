"""
Compress command: receives typed CLI arguments and dispatches to the service.
"""
from pathlib import Path
from typing import Optional
from pdfc.domain.models import CompressionSettings
from pdfc.cli.output import OutputView
from pdfc.cli.input import InputView
from pdfc.services.compression_service import CompressionService


class CompressCommand:
    """
    CLI command for compressing a PDF file.

    Receives typed arguments from the CLI layer, builds the compression
    settings, delegates processing to the service and displays the result
    via the output view. Contains no business logic.

    Attributes
    ----------
    _service : CompressionService
        Service layer for executing the compression.
    _output : OutputView
        View for displaying output to the user.
    _input : InputView
        View for collecting input from the user in interactive mode.
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
        threshold: Optional[int],
        sharpen: Optional[float],
        contrast: Optional[float],
        unsharp_mask: bool,
        png_compression_level: Optional[int],
        tiff_ccitt: bool,
        verbose: bool,
    ) -> None:
        """
        Runs the compress command.
        """
        if interactive:
            settings = self._run_interactive_mode()
        else:
            settings = self._run_cli_mode(
                mode=mode,
                dpi=dpi,
                jpeg_quality=jpeg_quality,
                threshold=threshold,
                sharpen=sharpen,
                contrast=contrast,
                unsharp_mask=unsharp_mask,
                png_compression_level=png_compression_level,
                tiff_ccitt=tiff_ccitt,
            )

        try:
            self._service.process(settings)
        except ValueError as e:
            self._output.show_error(str(e))
            return

        self._output.show_success('Compression settings are valid.')
        self._output.print_input_values(settings)

    def _run_cli_mode(
        self,
        mode: Optional[str],
        dpi: Optional[int],
        jpeg_quality: Optional[int],
        threshold: Optional[int],
        sharpen: Optional[float],
        contrast: Optional[float],
        unsharp_mask: bool,
        png_compression_level: Optional[int],
        tiff_ccitt: bool,
    ) -> CompressionSettings:
        """
        Builds CompressionSettings from typed CLI arguments.

        Returns
        -------
        CompressionSettings
            The compression settings built from the CLI arguments.
        """
        try:
            return CompressionSettings(
                _mode=mode,
                _dpi=dpi,
                _jpeg_quality=jpeg_quality,
                _bw_threshold=threshold,
                _sharpen=sharpen,
                _contrast=contrast,
                _unsharp_mask=unsharp_mask,
                _png_compression=png_compression_level,
                _tiff_ccitt=tiff_ccitt,
            )
        except Exception as e:
            self._output.show_error(f'An error occurred: {str(e)}')
            raise

    def _run_interactive_mode(self) -> CompressionSettings:
        """
        Collects CompressionSettings interactively via prompts.

        Returns
        -------
        CompressionSettings
            The compression settings built from user input.
        """
        try:
            self._output.show_info('Starting interactive mode...\n')
            mode = self._input.prompt_mode()
            dpi = self._input.prompt_dpi()
            jpeg_quality = self._input.prompt_jpeg_quality()
            png_compression = self._input.prompt_png_compression()
            bw_threshold = self._input.prompt_bw_threshold()
            sharpen = self._input.prompt_sharpen()
            contrast = self._input.prompt_contrast()
            unsharp_mask = self._input.prompt_unsharp_mask()
            tiff_ccitt = self._input.prompt_tiff_ccitt()
        except KeyboardInterrupt:
            self._output.show_info('\nInteractive mode cancelled.')
            raise
        except Exception as e:
            self._output.show_error(f'An error occurred: {str(e)}')
            raise

        return CompressionSettings(
            _mode=mode,                        # type: ignore
            _dpi=dpi,
            _jpeg_quality=jpeg_quality,
            _bw_threshold=bw_threshold,
            _sharpen=sharpen,
            _contrast=contrast,
            _unsharp_mask=unsharp_mask,
            _png_compression=png_compression,
            _tiff_ccitt=tiff_ccitt,
        )
