from mlm_doc_parser import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fcapy.context import FormalContext
from fcapy.lattice import *
from fcapy.visualizer import LineVizNx

class FormalConceptAnalysis:

    def __init__(self, mlm: MlmDoc):
        self.mlm = mlm
        self.object_labels = [] # initialized as empty array
        self.attribute_labels = [] # initialized as empty array
        self.incidence_relation = np.array([]) # initialized as empty array
        self.formal_context = FormalContext()
        self.concept_lattice:ConceptLattice

    def perform_promotion(self):
        self.get_fc_labels()
        self.construct_incidence_relation()
        self.construct_formal_context()
        self.concept_lattice = ConceptLattice.from_context(self.formal_context)

    def conceptual_scaling(self):
        print("TBD: Dynamically formulate adjust FC")

    def get_fc_labels(self):
        # STEP 1: Extract Object Labels and Attr Labels
        attr_duplicate: bool = False
        for mlm_object in self.mlm.mlm_objects:
            self.object_labels.append(mlm_object.name)
            for mlm_object_attribute in mlm_object.attr_list:
                attr_duplicate = False
                for fc_attribute in self.attribute_labels:
                    if mlm_object_attribute.attr_name == fc_attribute:
                        attr_duplicate = True
                if not attr_duplicate:
                    self.attribute_labels.append(mlm_object_attribute.attr_name)

    def construct_incidence_relation(self):
        #STEP 2: Construct formal context as numpy array
        i = 0
        new_row = []
        for mlm_object in self.mlm.mlm_objects:
            new_row = []
            for fc_attribute in self.attribute_labels:
                if fc_attribute in [attr.attr_name for attr in mlm_object.attr_list]:
                    new_row.append(1)
                else:
                    new_row.append(0)

            if i == 0: # only applies to first iteration, where vstack wont work
                self.incidence_relation = np.append(self.incidence_relation, new_row)
            else:
                self.incidence_relation = np.vstack([self.incidence_relation, new_row])
            i += 1
    def construct_formal_context(self):
        self.formal_context = FormalContext.from_pandas(pd.DataFrame(self.incidence_relation,
                                                                         columns=self.attribute_labels,
                                                                         index=self.object_labels)
                                                            .replace(to_replace=0, value=False)
                                                            .replace(to_replace=1, value=True))

    def show_concept_lattice(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        vsl = LineVizNx()
        vsl.draw_concept_lattice(self.concept_lattice, ax=ax, flg_node_indices=True)
        # ax.set_title("Whatever", fontsize=18)
        plt.tight_layout()
        plt.show()

    def get_new_mlm_objects(self):
        new_mlm_objects = []

        for formal_concept_index in range(self.concept_lattice.bottom+1):
            fc_intent = self.concept_lattice.get_concept_new_intent(formal_concept_index)
            fc_extent = self.concept_lattice.get_concept_new_extent(formal_concept_index)

            if len(fc_extent) != 1 and len(fc_intent) > 0:
                print(f"\n----------CANDIDATE MLM CLASS DETECTED----------\nFC INDEX {formal_concept_index}\n"
                      f"EXTENSION: {fc_extent}\nINTENSION: {fc_intent}")


