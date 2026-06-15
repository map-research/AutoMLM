from src.fmmlx_mlm_structure.fm_multi_level_model import *
from src.fmmlx_mlm_structure.precedence_graph import PrecedenceGraph


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

    def perform_property_precedence_analysis(self, print_slot_collectives: bool = False,
                                             print_attribute_relations: bool = True,
                                             print_slot_comparisons: bool = True):
        """
        The core of property precedence analysis lies in the specification of slot collectives. Accessing the
        object sets of a slot collective, allows comparing slot collectives. The built-in set comparisons from Python
        here already return the precedence relation between two slot collectives.

        After having created the slot collectives, the main task is to compare all slot collectives of the
        given attributes in order to induce the precedence relation between attributes.
        """
        print_any: bool = print_slot_collectives | print_attribute_relations | print_slot_comparisons
        for flat_class in self.flat_classes:
            if print_any:
                print("PROPERTY PRECEDENCE ANALYSIS FOR " + flat_class.object_name + "\n")
            flat_class.create_slot_collectives(ignore_case=True, print_progress=print_slot_collectives)
            flat_class.analyze_attribute_precedence(print_attr_relations=print_attribute_relations,
                                                    print_slots=print_slot_comparisons)
            precedence_graph: PrecedenceGraph = flat_class.precedence_graph.get_precedence_graph()
            precedence_graph.set_inst_levels_for_properties()
            if precedence_graph.has_deepening_potential():

            if print_any:
                print("\n-------------------------------------------------------------------\n")


        print("DONE")
        return self.original_model

    def perform_deepening_operations_for_class(self, flat_class: FmmlxObject):
        """This method performs the required change operations on the output model, the original model remains
        unchanged. Currently tailored to property-precedence analysis only, needs to be tailored to further
        deepening analysis techniques"""
        assert flat_class.level == 1, "Change operations performed on L1 classes only"
        assert flat_class.precedence_graph is not None, ("Precedence graph not detected, "
                                                         "precedence analysis must be performed first")
        flat_class.promote_to_level_x(flat_class.get_precedence_graph().get_max_level() + 1)
        # max level returns max inst level, class must be one level higher
        for attr in flat_class.get_all_attributes():
            attr.set_inst_level(attr.get_proposed_inst_level())


