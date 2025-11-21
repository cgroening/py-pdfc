"""
Main controller coordinating between model and views.
"""
import argparse
from models.person_model import Person, PersonProcessor
from views.output_view import OutputView
from views.input_view import InputView


class MainController:
    """
    Main controller for the CLI application.

    Coordinates between the model and views, handles both
    CLI and interactive modes.
    """

    def __init__(self):
        """Initialize controller with parser and views."""
        self.program_name = \
            'Person Transformer'
        self.usage = \
            'Transform person names to upper or lower case'
        self.description = \
            'This program takes subcommands and command line arguments.'
        self.epilog = \
            'Use -i for interactive mode or -h for help.'

        self.output_view = OutputView()
        self.input_view = InputView()
        self.parser = self._init_parser()

    def _init_parser(self) -> argparse.ArgumentParser:
        """
        Initialize the argument parser.

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

        # Create subparsers for upper/lower commands
        subparsers = parser.add_subparsers(
            title='Sub commands',
            description='Available transformation commands',
            dest='subcommand'
        )

        # Add upper and lower subparsers
        for cmd in ['upper', 'lower']:
            subparser = subparsers.add_parser(
                cmd,
                help=f'Transform name to {cmd}case'
            )
            self._add_common_arguments(subparser)

        return parser

    def _add_common_arguments(self, parser: argparse.ArgumentParser):
        """
        Add common arguments to a parser.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Parser to add arguments to
        """
        parser.add_argument(
            'name',
            help='The full name',
            type=str
        )
        parser.add_argument(
            '-a',
            '--age',
            help='Age of the person',
            type=int,
            required=False
        )
        parser.add_argument(
            '-c',
            '--cars',
            help='Car brands',
            nargs='*',
            type=str,
            required=False
        )
        parser.add_argument(
            '-v',
            '--verbose',
            help='Verbose output',
            action='store_true',
            required=False
        )

    def run(self):
        """Main entry point: parse args and route to appropriate handler."""
        args = self.parser.parse_args()

        if args.interactive:
            self._run_interactive_mode()
        else:
            self._run_cli_mode(args)

    def _run_interactive_mode(self):
        """Handle interactive mode with questionary prompts."""
        try:
            self.output_view.show_info('Starting interactive mode...\n')

            # Collect input via prompts
            mode = self.input_view.prompt_mode()
            name = self.input_view.prompt_name()
            age = self.input_view.prompt_age()
            cars = self.input_view.prompt_cars()
            verbose = self.input_view.prompt_verbose()

            # Create model and process
            person = Person(name=name, age=age, cars=cars)
            processor = PersonProcessor(person, mode)
            result = processor.process()

            # Display result
            self.output_view.show_result(result, verbose)
        except KeyboardInterrupt:
            self.output_view.show_info('\nInteractive mode cancelled.')
        except Exception as e:
            self.output_view.show_error(f'An error occurred: {str(e)}')

    def _run_cli_mode(self, args):
        """
        Handle CLI mode with command line arguments.

        Parameters
        ----------
        args : argparse.Namespace
            Parsed command line arguments
        """
        try:
            # Check if subcommand was provided
            if not args.subcommand:
                self.parser.print_help()
                return

            # Create model from CLI arguments
            person = Person(
                name=args.name,
                age=args.age,
                cars=args.cars
            )

            # Process data
            processor = PersonProcessor(person, args.subcommand)
            result = processor.process()

            # Display result
            self.output_view.show_result(result, args.verbose)

        except Exception as e:
            self.output_view.show_error(f'An error occurred: {str(e)}')
