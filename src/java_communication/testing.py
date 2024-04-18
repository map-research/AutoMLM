"""
testing.py used to test AutoMLM scenarios such as XML parsing and writing
"""

from mlm_doc_parser import *

mlm_simple = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\gen_example.xml")
mlm_complex = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\warehouse_enhanced.xml")
mlm = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\examMgmt.xml")

print(mlm)
# print(mlm_complex)
