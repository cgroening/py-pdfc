"""
Interactive input view using Questionary.
"""
import questionary
from typing import Optional


class InputView:
    """Handles interactive input using Questionary."""

    CAR_BRANDS = [
        'Audi',
        'BMW',
        'Ford',
        'Honda',
        'Mercedes',
        'Toyota',
        'Volkswagen',
        'Volvo',
        'No cars'
    ]

    def prompt_mode(self) -> str:
        """
        Prompt for transformation mode.

        Returns
        -------
        str
            Selected mode ('upper' or 'lower')
        """
        return questionary.select(
            'How should the name be transformed?',
            choices=['upper', 'lower']
        ).ask()

    def prompt_name(self) -> str:
        """
        Prompt for name input.

        Returns
        -------
        str
            The entered name
        """
        return questionary.text(
            'Enter the full name:',
            validate=lambda text: len(text) > 0 or 'Name cannot be empty'
        ).ask()

    def prompt_age(self) -> Optional[int]:
        """
        Prompt for age input.

        Returns
        -------
        Optional[int]
            The entered age or None if skipped
        """
        age_str = questionary.text(
            'Enter age (press Enter to skip):',
            validate=lambda text: text == '' or text.isdigit()
                                  or 'Age must be a number'
        ).ask()

        return int(age_str) if age_str else None

    def prompt_cars(self) -> Optional[list[str]]:
        """
        Prompt for car selection.

        Returns
        -------
        Optional[list[str]]
            List of selected cars or None if 'No cars' was selected
        """
        cars = questionary.checkbox(
            'Select car brands (use Space to select, Enter to confirm):',
            choices=self.CAR_BRANDS
        ).ask()

        if not cars or 'No cars' in cars:
            return None

        return cars

    def prompt_verbose(self) -> bool:
        """
        Prompt for verbose mode.

        Returns
        -------
        bool
            True if verbose mode is selected
        """
        return questionary.confirm(
            'Show verbose output?',
            default=False
        ).ask()
