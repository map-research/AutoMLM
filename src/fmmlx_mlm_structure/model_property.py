from abc import ABCMeta, abstractmethod

from src.fmmlx_mlm_structure.model_element import ModelElement


class ModelProperty(ModelElement, metaclass=ABCMeta):
    """This class serves as an abstract superclass for all model properties (attributes-association ends,
    slots-slot links, constraints, operations). A property is a specific kind of modle element.
    Each property may access its owner."""

    def __init__(self, name, print_name):
        super().__init__(name=name, print_name=print_name)

