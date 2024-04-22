"""
testing.py used to test AutoMLM scenarios such as XML parsing and writing
"""

from mlm_class import *

#mlm_simple = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\gen_example.xml")
#mlm_complex = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\warehouse_enhanced.xml")
#mlm = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\examMgmt.xml")

# print(mlm)
# print(mlm_complex)

warehouseMLM = MultilevelModel("C:\\Programme"
                               "\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\warehouse_enhanced.xml")

# examMgmt = MultilevelModel("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\examMgmt.xml")

print(warehouseMLM)
