"""
testing.py used to test AutoMLM scenarios such as XML parsing and writing
"""

from datetime import datetime
from mlm_class import *
from lexicographicAnalysis import LexicalAnalysisHelper
from nltk.corpus import wordnet as wn

#mlm_simple = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\gen_example.xml")
#mlm_complex = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\warehouse_enhanced.xml")
#mlm = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\examMgmt.xml")

# print(mlm)
# print(mlm_complex)


# examMgmt = MultilevelModel("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\examMgmt.xml")


print(datetime.now())

gen_example = MultilevelModel("C:\\Users\\fhend\\Documents\\GitHub_Repos\\MosaicFX\\AutoMLM\\mlm_files\\gen_example.xml")




helper = LexicalAnalysisHelper()

sim = helper.getSimilarityOfLabels("Fence", "Tom climbed a jam")


print(sim)

















"""
objs = gen_example.mlm_objects

for o in objs:
    o.automaticSemanticMatching()


print(datetime.now())
for o1 in objs:
    for o2 in objs:
        if o1 is o2:
            continue

        #print(o1.name)
        #print(o2.name)
        print(datetime.now())
        c = helper.getCommonHypernyms(o1, o2)
        print(f'{o1.name} and {o2.name}:\t{c}')
        """



print(datetime.now())