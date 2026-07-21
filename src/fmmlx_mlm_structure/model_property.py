from abc import ABC, abstractmethod

from src.fmmlx_mlm_structure.model_element import ModelElement


class ModelProperty(ModelElement, ABC):
    """This class serves as an abstract superclass for all model properties (attributes-association ends,
    slots-slot links, constraints, operations). A property is a specific kind of modle element.
    Each property may access its owner."""

    def __init__(self, print_name: str):
        super().__init__()
        self.print_name = print_name

    def get_print_name(self):
        return self.print_name

    def set_print_name(self, print_name: str):
        self.print_name = print_name
