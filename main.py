#!/usr/bin/env python3
"""
MVC CLI Application with Rich and Questionary

A command line program demonstrating MVC architecture with:
- Rich for beautiful output formatting
- Questionary for interactive input
- Support for both CLI and interactive modes

Examples
--------
CLI Mode:
    python main.py upper "Corvin Gröning" -a 36 -c Ford Honda
    python main.py upper "Corvin Gröning" -a 36 -c Ford Honda -v
    python main.py lower "Corvin Gröning" -a 36 -c Ford Honda -v
    python main.py upper Corvin
    python main.py lower Corvin

Interactive Mode:
    python main.py -i
    
Help:
    python main.py -h
"""
from controllers.main_controller import MainController


def main():
    """Entry point for the application."""
    controller = MainController()
    controller.run()


if __name__ == '__main__':
    main()
