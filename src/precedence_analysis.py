"""
Instances of this class serve to coordinate/execute the precedence analysis. The core idea of the precedence analysis
can be described as follows:
1. identify and construct slot collectives
2. compare scope of slot collectives to determine precedence relation between each
3. perform inductive leap: apply precedence relation from slots to attributes

Following property precedence analysis, a number of change operations can be performed to realize the model deepening
"""
from src.fmmlx_mlm_structure.fm_multi_level_model import *


class PrecedenceAnalysis:
    def __init__(self, input_model: FmmlxModel):
        self.input_model: FmmlxModel = input_model
        self.flat_classes: [FmmlxObject] = input_model.get_all_flat_classes()
        self.pure_objects: [FmmlxObject] = input_model.get_all_pure_objects()

    def perform_precedence_analysis(self):
        return None
        # TODO

    def create_slot_collectives_for_class(self):
