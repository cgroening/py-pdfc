import argparse
from pdfc.cli.output import OutputView
from pdfc.cli.input import InputView
from pdfc.cli.commands.compress import CompressCommand
from pdfc.services.compression_service import CompressionService


def _build_parser() -> argparse.ArgumentParser:
    """Builds and returns the argument parser."""
    parser = argparse.ArgumentParser(
        prog='pdfc',
        usage='pdfc [-i] [options] input_path [output_path]',
        description=(
            'Compress and optimize PDF files using various algorithms and '
            'settings.'
        ),
        epilog='Use -i for interactive mode or -h for help.',
    )

    parser.add_argument(
        '-i', '--interactive',
        help='Start in interactive mode',
        action='store_true',
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Verbose output',
        action='store_true',
        required=False,
    )
    parser.add_argument(
        '-m', '--mode',
        help='Compression mode (color, gray, bw)',
        type=str,
        required=False,
    )
    parser.add_argument(
        '-d', '--dpi',
        help='DPI - resolution for image downsampling',
        type=int,
        required=False,
    )
    parser.add_argument(
        '-q', '--jpeg-quality',
        help='Compression quality for JPEG (1-100)',
        type=int,
        required=False,
    )
    parser.add_argument(
        '-t', '--threshold',
        help='Threshold for black and white conversion (0-255)',
        type=int,
        required=False,
    )
    parser.add_argument(
        '-s', '--sharpen',
        help='Sharpening filter (0.0 to 3.0)',
        type=float,
        required=False,
    )
    parser.add_argument(
        '-c', '--contrast',
        help='Contrast (0.0 to 3.0)',
        type=float,
        required=False,
    )
    parser.add_argument(
        '-u', '--unsharp_mask',
        help='Apply unsharp mask filter to enhance sharpness',
        action='store_true',
        required=False,
    )
    parser.add_argument(
        '-p', '--png-compression-level',
        help=(
            'PNG compression level (0–9, higher values reduce file size but '
            'increase processing time); if not set, JPEG is used'
        ),
        type=int,
        required=False,
    )
    parser.add_argument(
        '-T', '--tiff-ccitt',
        help='Use TIFF with CCITT Group 4 compression for BW images',
        action='store_true',
        required=False,
    )
    parser.add_argument(
        'input_path',
        help='Path to the input PDF file',
    )
    parser.add_argument(
        'output_path',
        help='Path to the output file (automatically set if not provided)',
        nargs='?',
        default=None,
    )

    return parser


def main() -> None:
    """Entry point: parse args, wire dependencies and run the command."""
    # Dependency composition (Composition Root)
    output = OutputView()
    input_view = InputView()
    service = CompressionService()
    command = CompressCommand(service, output, input_view)

    # Parse and dispatch
    parser = _build_parser()
    args = parser.parse_args()
    command.run(args)


if __name__ == '__main__':
    main()
