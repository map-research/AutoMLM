from mlm_doc_parser import *


# this function is executed when the "execute" button is hit
def perform_promotion_process(file_path: str):
    mlm = MlmDoc(file_path)
    print(mlm)


def perform_fca_promotion():
    print("FCA Promotion Analysis initiated")
