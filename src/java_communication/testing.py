"""
testing.py used to test AutoMLM scenarios such as XML parsing and writing
"""

from datetime import datetime
from lexical_analysis import LexicalAnalysis
from mlm_class import *
from lexical_analysis_helper import LexicalAnalysisHelper
from nltk.corpus import wordnet as wn

#mlm_simple = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\gen_example.xml")
#mlm_complex = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\warehouse_enhanced.xml")
#mlm = MlmDoc("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\examMgmt.xml")

# print(mlm)
# print(mlm_complex)


# examMgmt = MultilevelModel("C:\\Programme\\XModeler-AutoMLM-v1\\XModeler\\AutoMLM\\mlm_files\\examMgmt.xml")

"""
print(datetime.now())

gen_example = MultilevelModel("C:\\Users\\fhend\\Documents\\GitHub_Repos\\MosaicFX\\AutoMLM\\mlm_files\\gen_example.xml")




helper = LexicalAnalysisHelper()



















objs = gen_example.mlm_objects

for o in objs:
    o.automaticSemanticMatching()


for o1 in objs:
    for o2 in objs:
        if o1 is o2:
            continue

        #print(o1.name)
        #print(o2.name)
        #print(datetime.now())
        c = helper.getCommonHypernyms(o1, o2)
        c = helper._reduceSetOfHypernyms(c)
        cstr = f'{o1.name} and {o2.name}'
        print(cstr.ljust(50,' '), [a[0] for a in c])
        



print(datetime.now())
"""



"""

o1 = model.mlm_objects[1]

a1 = o1.attr_list[1]


print(a1.lexemes)

"""



model = MultilevelModel('ExampleModels/01_GA/rcvickiydreizwei.xml')



analyser = LexicalAnalysis(model, 'GA', 3,3,0.5,-0.5)    

analyser.perform_Analysis()
