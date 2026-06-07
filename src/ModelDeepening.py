from src.fmmlx_mlm_structure.fm_multi_level_model import *


class ModelDeepening:

    # init only accepts single MLM file currently, may be expanded to multiple files in the future
    def __init__(self, input_model: FmmlxModel = None):
        self.original_model: FmmlxModel = input_model
        self.output_model: FmmlxModel = input_model
        self.flat_classes: [FmmlxObject] = []
        self.pure_objects: [FmmlxObject] = []

    """
    The following sets of methods specify getters and setters for the transformed models.
    """

    def set_input_model(self, input_model: FmmlxModel):
        assert self.original_model is None, "Original model already specified"
        self.original_model: FmmlxModel = input_model
        self.output_model: FmmlxModel = input_model
        self.flat_classes: [FmmlxObject] = input_model.get_all_flat_classes()
        self.pure_objects: [FmmlxObject] = input_model.get_all_pure_objects()

    def get_original_model(self) -> FmmlxModel:
        return self.original_model

    def get_output_model(self) -> FmmlxModel:
        return self.output_model

    def set_output_model(self, output_model: FmmlxModel):
        self.output_model = output_model

    def export_multi_level_model_as_xml(self):
        assert self.output_model is not None, "No output model is specified"
        self.output_model.export_xml()

    """
    The following methods specify the various model-deepening analysis methods.
    """

    """
    Instances of this class serve to coordinate/execute the precedence analysis. 
    The core idea of the precedence analysis can be described as follows:
    1. identify and construct slot collectives
    2. compare scope of slot collectives to determine precedence relation between each
    3. perform inductive leap: apply precedence relation from slots to attributes
    """

    def perform_property_precedence_analysis(self):
        """
        The core of property precedence analysis lies in the specification of slot collectives. Accessing the
        object sets of a slot collective, allows comparing slot collectives. The built-in set comparisons from Python
        here already return the precedence relation between two slot collectives.

        After having created the slot collectives, the main task is to compare all slot collectives of the
        given attributes in order to induce the precedence relation between attributes.
        """
        for flat_class in self.flat_classes:
            flat_class.create_slot_collectives(ignore_case=True)
            flat_class.analyze_attribute_precedence()


        print("DONE")
        return self.original_model
