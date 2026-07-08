from abc import ABC, abstractmethod


class ModelProperty(ABC):
    """This class serves as a shell superclass"""

    def __init__(self, print_name: str):
        self.print_name = print_name

    def get_print_name(self):
        return self.print_name

    def set_print_name(self, print_name: str):
        self.print_name = print_name
