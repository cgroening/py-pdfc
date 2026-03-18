"""
pdfc - PDF Compressor

Entry point and composition root: wires all layers together and dispatches
to the compress command.

Examples
--------
CLI Mode:
    pdfc input.pdf output.pdf -m bw -d 300

Interactive Mode:
    pdfc -i input.pdf

Help:
    pdfc --help
"""
import typer
from pathlib import Path
from typing import Optional
from pdfc.cli.output import OutputView
from pdfc.cli.input import InputView
from pdfc.cli.commands.compress import CompressCommand
from pdfc.services.compression_service import CompressionService


app = typer.Typer(
    help='Compress and optimize PDF files using various algorithms and settings.',
    epilog='Use -i for interactive mode or --help for help.',
)


# Dependency composition (Composition Root)
_output = OutputView()
_input_view = InputView()
_service = CompressionService()
_command = CompressCommand(_service, _output, _input_view)


@app.command()
def compress(
    input_path: Path = typer.Argument(
        ...,
        help='Path to the input PDF file',
    ),
    output_path: Optional[Path] = typer.Argument(
        None,
        help='Path to the output file (automatically set if not provided)',
    ),
    interactive: bool = typer.Option(
        False, '-i', '--interactive',
        help='Start in interactive mode',
    ),
    verbose: bool = typer.Option(
        False, '-v', '--verbose',
        help='Verbose output',
    ),
    mode: Optional[str] = typer.Option(
        None, '-m', '--mode',
        help='Compression mode (color, gray, bw)',
    ),
    dpi: Optional[int] = typer.Option(
        None, '-d', '--dpi',
        help='DPI - resolution for image downsampling',
    ),
    jpeg_quality: Optional[int] = typer.Option(
        None, '-q', '--jpeg-quality',
        help='Compression quality for JPEG (1-100)',
    ),
    threshold: Optional[int] = typer.Option(
        None, '-t', '--threshold',
        help='Threshold for black and white conversion (0-255)',
    ),
    sharpen: Optional[float] = typer.Option(
        None, '-s', '--sharpen',
        help='Sharpening filter (0.0 to 3.0)',
    ),
    contrast: Optional[float] = typer.Option(
        None, '-c', '--contrast',
        help='Contrast (0.0 to 3.0)',
    ),
    unsharp_mask: bool = typer.Option(
        False, '-u', '--unsharp-mask',
        help='Apply unsharp mask filter to enhance sharpness',
    ),
    png_compression_level: Optional[int] = typer.Option(
        None, '-p', '--png-compression-level',
        help=(
            'PNG compression level (0-9, higher values reduce file size but '
            'increase processing time); if not set, JPEG is used'
        ),
    ),
    tiff_ccitt: bool = typer.Option(
        False, '-T', '--tiff-ccitt',
        help='Use TIFF with CCITT Group 4 compression for BW images',
    ),
):
    _command.run(
        interactive=interactive,
        input_path=input_path,
        output_path=output_path,
        mode=mode,
        dpi=dpi,
        jpeg_quality=jpeg_quality,
        threshold=threshold,
        sharpen=sharpen,
        contrast=contrast,
        unsharp_mask=unsharp_mask,
        png_compression_level=png_compression_level,
        tiff_ccitt=tiff_ccitt,
        verbose=verbose,
    )


def main() -> None:
    app()


if __name__ == '__main__':
    main()
