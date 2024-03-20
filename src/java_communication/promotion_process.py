from mlm_doc_parser import *
from fca_promotion import *


# this function is executed when the "execute" button is hit
def perform_promotion_process(file_path: str, automation_technique, case):
    mlm = MlmDoc(file_path)
    print(mlm)

    if automation_technique == "Formal Concept Analysis":
        fca = FormalConceptAnalysis(mlm)
        fca.perform_promotion()
        print(fca.object_labels)
        print(fca.attribute_labels)
        print(fca.incidence_relation)
        print(fca.formal_context)

        fca.show_concept_lattice()
        fca.get_new_mlm_objects()

    else:
        print("WRONG AUTOMATION TECHNIQUE SELECTED")

# mlm = MlmDoc("mlm_files/gen_example.xml")
# mlm = MlmDoc.input()
# print(mlm)


# perform_promotion_process("mlm_files/gen_example.xml", "Formal Concept Analysis", "n")