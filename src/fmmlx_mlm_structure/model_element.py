from abc import ABC


class ModelElement(ABC):
    """The abstract class ModelElement serves as a superclass to any element (property or entity) contained in a model.
    This generalization is required for change suggestions in model deepening"""
    def __init__(self):
        pass

    def get_model_element_type(self) -> str:
        return type(self).__name__.lower()
