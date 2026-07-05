from src.fmmlx_mlm_structure.model_property_enum import ModelPropertyEnum
from src.fmmlx_mlm_structure.precedence_graph import PropertyPrecedenceGraph


class SlotPrecedenceGraph(PropertyPrecedenceGraph):
    def __init__(self):
        super().__init__()
        self.property_type: ModelPropertyEnum = ModelPropertyEnum.SLOT
        