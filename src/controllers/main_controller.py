"""
Main controller coordinating between model and views.
"""
import argparse
from models.compression_settings_model import CompressionSettings
from views.output_view import OutputView
from views.input_view import InputView


class MainController:
    """
    Main controller that is called by the entry point script.

    Attributes
    ----------
    program_name : str
        Name of the program.
    usage : str
        Usage string for the program.
    description : str
        Description of the program.
    epilog : str
        Epilog text for the program.
    output_view : OutputView
        View for displaying output to the user.
    input_view : InputView
        View for collecting input from the user.
    parser : argparse.ArgumentParser
        Argument parser for command line arguments.

    """

    program_name: str
    usage: str
    description: str
    epilog: str
    output_view: OutputView
    input_view: InputView
    parser: argparse.ArgumentParser


    def __init__(self):
        """Initialize controller with parser and views."""
        self.program_name = \
            'pdfc'
        self.usage = \
            'pdfc [-i] <subcommand> [options]'
        self.description = \
            '''Compress and optimize PDF files using various algorithms and settings.'''
        self.epilog = \
            'Use -i for interactive mode or -h for help.'

        self.output_view = OutputView()
        self.input_view = InputView()
        self.parser = self._init_parser()
        self._add_arguments_for_compression_settings()

    def _init_parser(self) -> argparse.ArgumentParser:
        """
        Initializes the argument parser.

        Returns
        -------
        argparse.ArgumentParser
            Configured parser
        """
        parser = argparse.ArgumentParser(
            prog=self.program_name,
            usage=self.usage,
            description=self.description,
            epilog=self.epilog
        )

        # Add interactive mode flag to main parser
        parser.add_argument(
            '-i',
            '--interactive',
            help='Start in interactive mode',
            action='store_true'
        )

        # Flag for verbose output
        parser.add_argument(
            '-v',
            '--verbose',
            help='Verbose output',
            action='store_true',
            required=False
        )

        return parser

    def _add_arguments_for_compression_settings(self):
        """
        Adds arguments for the compression settings.

        """
        parser = self.parser
        parser.add_argument(
            '-m',
            '--mode',
            help='Compression mode (color, gray, bw)',
            type=str,
            required=False
        )
        parser.add_argument(
            '-d',
            '--dpi',
            help='DPI - resolution for image downsampling',
            type=int,
            required=False
        )
        parser.add_argument(
            '-q',
            '--jpeg-quality',
            help='Compression quality for JPEG (1-100)',
            type=int,
            required=False
        )
        parser.add_argument(
            '-t',
            '--threshold',
            help='Threshold for black and white conversion (0-255)',
            type=int,
            required=False
        )
        parser.add_argument(
            '-s',
            '--sharpen',
            help='Sharpening filter (0.0 to 3.0)',
            type=float,
            required=False
        )
        parser.add_argument(
            '-c',
            '--contrast',
            help='Contrast (0.0 to 3.0)',
            type=float,
            required=False
        )
        parser.add_argument(
            '-u',
            '--unsharp_mask',
            help='Apply unsharp mask filter to enhance sharpness',
            action='store_true',
            required=False
        )
        parser.add_argument(
            '-p',
            '--png-compression-level',
            help='''PNG compression level (0–9, higher values reduce file
            size but increase processing time); if not set, JPEG is used''',
            type=int,
            required=False
        )
        parser.add_argument(
            '-T',
            '--tiff-ccitt',
            help='Use TIFF with CCITT Group 4 compression for BW images',
            action='store_true',
            required=False
        )
        parser.add_argument(
            'input_path',
            help='Path to the input PDF file',
        )
        parser.add_argument(
            'output_path',
            help='Path to the output file (automatically set if not provided)',
            nargs='?',  # Optional
            default=None
        )

    def run(self):
        """Main entry point: parse args and route to appropriate handler."""
        args = self.parser.parse_args()

        if args.interactive:
            self._run_interactive_mode()
        else:
            self._run_cli_mode(args)

    # def _run_interactive_mode(self):
    #     """Handles interactive mode with questionary prompts."""

    #     # TODO:

    #     try:
    #         self.output_view.show_info('Starting interactive mode...\n')

    #         # Collect input via prompts
    #         mode = self.input_view.prompt_mode()
    #         name = self.input_view.prompt_name()
    #         age = self.input_view.prompt_age()
    #         cars = self.input_view.prompt_cars()
    #         verbose = self.input_view.prompt_verbose()

    #         # Create model and process
    #         person = CompressionSettings(name=name, age=age, cars=cars)
    #         processor = PersonProcessor(person, mode)
    #         result = processor.process()

    #         # Display result
    #         self.output_view.show_result(result, verbose)
    #     except KeyboardInterrupt:
    #         self.output_view.show_info('\nInteractive mode cancelled.')
    #     except Exception as e:
    #         self.output_view.show_error(f'An error occurred: {str(e)}')

    def _run_cli_mode(self, args):
        """
        Handles CLI mode with command line arguments.

        Parameters
        ----------
        args : argparse.Namespace
            Parsed command line arguments
        """
        try:
            # Create model from CLI arguments
            compression_settings = CompressionSettings(
                _mode=args.mode,
                _dpi=args.dpi,
                _jpeg_quality=args.jpeg_quality,
                _bw_threshold=args.threshold,
                _sharpen=args.sharpen,
                _contrast=args.contrast,
                _unsharp_mask=args.unsharp_mask,
                _png_compression=args.png_compression_level,
                _tiff_ccitt=args.tiff_ccitt
            )

            compression_settings.validate()
            self.output_view.show_success('Compression settings are valid.')
            self.output_view.print_compression_settings(compression_settings)

            # TODO: file path(s)

            # # Process data
            # processor = PersonProcessor(person, args.subcommand)
            # result = processor.process()

            # # Display result
            # self.output_view.show_result(result, args.verbose)

        except Exception as e:
            self.output_view.show_error(f'An error occurred: {str(e)}')
