import typer
from pathlib import Path
from typing import Optional

from pdfc.cli.compress_parameters import CompressRequest
from pdfc.cli.input import InputView
from pdfc.cli.commands.compress import CompressCommand
from pdfc.cli.commands.compare import CompareCommand
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression_service import CompressionService
from pdfc.storage.pdf_compressor import PdfCompressor
from pdfc.storage.presets_storage import PresetsStorage


app = typer.Typer(
    help='Compress and optimise PDF files using various algorithms.',
    no_args_is_help=True,
)

# Dependency composition (Composition Root)
_compressor      = PdfCompressor()
_presets         = PresetsStorage()
_service         = CompressionService(_compressor, _presets)
_input_view      = InputView()
_compress_cmd    = CompressCommand(_service, _input_view)
_compare_cmd     = CompareCommand(_service,)


@app.command()
def compress(
    input_path: Path = typer.Argument(
        ...,
        help='PDF file or directory of PDF files to compress.',
        exists=True,
        file_okay=True,
        dir_okay=True,
        resolve_path=True,
    ),
    output_path: Optional[Path] = typer.Argument(
        None,
        help=(
            'Output file path (single-file mode only). '
            'Defaults to <input>-compressed.pdf.'
        ),
    ),
    interactive_mode: bool = typer.Option(
        False, '-i', '--interactive',
        help='Collect compression settings interactively.',
    ),
    mode: Optional[str] = typer.Option(
        None, '-m', '--mode',
        help='Compression mode: color | gray | bw.',
    ),
    dpi: Optional[int] = typer.Option(
        None, '-d', '--dpi',
        help='Resolution for rasterisation (dots per inch).',
    ),
    jpeg_quality: Optional[int] = typer.Option(
        None, '-q', '--jpeg-quality',
        help='JPEG quality 1–100. Mutually exclusive with --png-compression-level.',
    ),
    png_compression_level: Optional[int] = typer.Option(
        None, '-p', '--png-compression-level',
        help='PNG compression level 0–9. Mutually exclusive with --jpeg-quality.',
    ),
    threshold: Optional[int] = typer.Option(
        None, '-t', '--threshold',
        help='B&W threshold 0–255 (only used in bw mode).',
    ),
    sharpen: Optional[float] = typer.Option(
        None, '-s', '--sharpen',
        help='Sharpening factor 0.0–3.0 (0 = off).',
    ),
    contrast: Optional[float] = typer.Option(
        None, '-c', '--contrast',
        help='Contrast factor 0.0–3.0 (1.0 = no change).',
    ),
    unsharp_mask: bool = typer.Option(
        False, '-u', '--unsharp-mask',
        help='Apply PIL UnsharpMask filter.',
    ),
    tiff_ccitt: bool = typer.Option(
        False, '-T', '--tiff-ccitt',
        help='Use TIFF CCITT Group 4 as intermediate format (bw mode only).',
    ),
):
    if jpeg_quality is not None and png_compression_level is not None:
        raise typer.BadParameter(
            'Cannot use --jpeg-quality and --png-compression-level at the same time.'
        )

    compression_settings = CompressionSettings(
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
    compress_request = CompressRequest(
        interactive_mode=interactive_mode,
        input_path=input_path,
        output_path=output_path,
        compression_settings=compression_settings,
    )

    _compress_cmd.run(compress_request)


@app.command()
def compare(
    input_path: Path = typer.Argument(
        ...,
        help='PDF file or directory of PDF files to compare.',
        exists=True,
        file_okay=True,
        dir_okay=True,
        resolve_path=True,
    ),
    dpi: int = typer.Option(
        300, '-d', '--dpi',
        help='Resolution for rasterization (dots per inch). Default: 300.',
    )
):
    _compare_cmd.run(input_path=input_path, dpi=dpi)


def main() -> None:
    app()

