"""
pdfc - PDF Compressor

A command line program for compressing PDF files.

Examples
--------
CLI Mode:
    ...

Interactive Mode:
    ...

Help:
    ...
"""
from controllers.main_controller import MainController


def main():
    """Entry point for the application."""
    controller = MainController()
    controller.run()


if __name__ == '__main__':
    main()
