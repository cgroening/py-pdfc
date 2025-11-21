"""
Model for person data and business logic.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Person:
    """Data class for person information."""
    name: str
    age: Optional[int] = None
    cars: Optional[list[str]] = None

    def transform_name(self, mode: str) -> str:
        """
        Transform the name based on the mode.
        
        Parameters
        ----------
        mode : str
            Either 'upper' or 'lower'
            
        Returns
        -------
        str
            Transformed name
        """
        match mode:
            case 'upper':
                return self.name.upper()
            case 'lower':
                return self.name.lower()
            case _:
                return self.name


class PersonProcessor:
    """Business logic for processing person data."""
    
    def __init__(self, person: Person, mode: str):
        """
        Initialize the processor.
        
        Parameters
        ----------
        person : Person
            The person data to process
        mode : str
            The transformation mode ('upper' or 'lower')
        """
        self.person = person
        self.mode = mode
    
    def process(self) -> Person:
        """
        Process the person data.
        
        Returns
        -------
        Person
            Person with transformed name
        """
        transformed_name = self.person.transform_name(self.mode)
        return Person(
            name=transformed_name,
            age=self.person.age,
            cars=self.person.cars
        )
