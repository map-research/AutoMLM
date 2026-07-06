import datetime

from src.fmmlx_mlm_structure.attribute_precedence_graph import AttributePrecedenceGraph
from src.fmmlx_mlm_structure.fm_multi_level_model import *
from src.fmmlx_mlm_structure.image_file_format_enum import ImageFileFormat
from src.fmmlx_mlm_structure.precedence_graph import PropertyPrecedenceGraph


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
                                             print_attribute_relations: bool = False,
                                             print_slot_comparisons: bool = False,
                                             export_graphs_as_png: bool = False):
        """
        The core of property precedence analysis lies in the specification of slot collectives. Accessing the
        scopes of a slot collective allows comparing slot collectives. The built-in set comparisons from Python
        here already return the precedence relation between two slot collectives.

        After having created the slot collectives, the main task is to compare all slot collectives of the
        given attributes in order to induce the precedence relation between attributes.
        """
        print_any: bool = print_slot_collectives | print_attribute_relations | print_slot_comparisons
        for flat_class in self.flat_classes:
            if print_any:
                print("PROPERTY PRECEDENCE ANALYSIS FOR " + flat_class.object_name + "\n")
            flat_class.create_slot_collectives(ignore_case=True, print_progress=print_slot_collectives)
            flat_class.create_property_precedence_graphs(print_attr_relations=print_attribute_relations,
                                                         print_slots=print_slot_comparisons)
            attr_precedence_graph: AttributePrecedenceGraph = flat_class.get_attribute_precedence_graph()
            attr_precedence_graph.export_graph_as_image(flat_class.object_name, ImageFileFormat.PNG)
            spg = flat_class.get_slot_precedence_graph()
            spg.export_graph_as_image(flat_class.object_name, ImageFileFormat.PNG)

            #  attr_precedence_graph.set_inst_levels_for_attributes()
            if attr_precedence_graph.has_deepening_potential():
                #self.output_model.perform_change_operations_for_precedence_analysis(flat_class)
                print("\n---------------------OUTPUT MODEL------------------------")
                #print(self.output_model)
            if print_any:
                print("\n-------------------------------------------------------------------\n")
        print("DONE")
        return self.original_model

    def perform_deepening_operations_for_class(self, flat_class: FmmlxObject):
        """This method performs the required change operations on the output model, the original model remains
        unchanged. Currently tailored to property-precedence analysis only, needs to be tailored to further
        deepening analysis techniques"""
        assert flat_class.level == 1, "Change operations performed on L1 classes only"
        assert flat_class.attribute_precedence_graph is not None, ("Precedence graph not detected, "
                                                         "precedence analysis must be performed first")
        max_inst_level: int = flat_class.get_attribute_precedence_graph().get_max_level()
        flat_class.promote_to_level_x(max_inst_level + 1)
        flat_class.promote_attributes()
        print(flat_class)
        while max_inst_level >= 0:

            max_inst_level -= max_inst_level



