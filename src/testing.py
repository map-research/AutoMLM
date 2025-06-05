"""
testing.py used to test AutoMLM scenarios such as XML parsing and writing
"""

from datetime import datetime
from itertools import combinations
from lexical_analysis import LexicalAnalysis
from mlm_class import *
from lexical_analysis_helper import LexicalAnalysisHelper, LexicalAnalysisHelperBabelnet, LexicalAnalysisHelperWikidata
from nltk.corpus import wordnet as wn
import xlsxwriter


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



#model = MultilevelModel('ExampleModels/01_GA/rcvickiydreizwei.xml')



#analyser = LexicalAnalysis(model, 'GA', 3,3,0.5,-0.5)    

#analyser.perform_Analysis()


#isgraded/ungraded
def test_1():
    spacing = 40
    print(datetime.now())
    print('')

    helper = LexicalAnalysisHelper()

    ## generate attr
    attr1 = MlmAttr('isUngraded','Root::XCore::String',0)
    attr2 = MlmAttr('isGraded', 'Root::XCore::String',0)

    attr1.automaticSemanticMatching()
    attr2.automaticSemanticMatching()

    print(f'Len of {attr1.attr_name}:'.ljust(spacing,' '), f'{len(attr1.lexemes)}')
    print(f'Len of {attr2.attr_name}:'.ljust(spacing,' '), f'{len(attr2.lexemes)}')
    print('')
    print(f'Lex of {attr1.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr1.lexemes]}')
    print(f'Lex of {attr2.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr2.lexemes]}')
    print('')
    sim = helper.getSimilarityOfLexemeLabels(attr1.lexemes, attr2.lexemes)
    print(f'Lexeme Sim of {attr1.attr_name} and {attr2.attr_name}'.ljust(spacing, ' '), f'{round(sim,4)}')
    sim = helper.getSimilarityOfLabels(attr1.attr_name, attr2.attr_name)
    print(f'Label Sim of {attr1.attr_name} and {attr2.attr_name}'.ljust(spacing, ' '), f'{round(sim,4)}')

    print('')
    print(datetime.now())


#highestScore / maxPoints
def test_2():
    spacing = 35
    print(datetime.now())
    print('')

    helper = LexicalAnalysisHelper()

    ## generate attr
    attr1 = MlmAttr('highestScore','Root::XCore::String',0)
    attr2 = MlmAttr('maxPoints', 'Root::XCore::String',0)

    attr1.automaticSemanticMatching()
    attr2.automaticSemanticMatching()

    print(f'Len of {attr1.attr_name}:'.ljust(spacing,' '), f'{len(attr1.lexemes)}')
    print(f'Len of {attr2.attr_name}:'.ljust(spacing,' '), f'{len(attr2.lexemes)}')
    print('')
    print(f'Lex of {attr1.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr1.lexemes]}')
    print(f'Lex of {attr2.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr2.lexemes]}')
    print('')
    sim = helper.getSimilarityOfLexemeLabels(attr1.lexemes, attr2.lexemes)
    print(f'Sim of {attr1.attr_name} and {attr2.attr_name}'.ljust(spacing, ' '), f'{round(sim,4)}')

    print('')
    print(datetime.now())


#lengthinminutes/durationInMinutes
def test_3():
    spacing = 35
    print(datetime.now())
    print('')

    helper = LexicalAnalysisHelper()

    ## generate attr
    attr1 = MlmAttr('lengthInMinutes','Root::XCore::String',0)
    attr2 = MlmAttr('durationInMinutes', 'Root::XCore::String',0)

    attr1.automaticSemanticMatching()
    attr2.automaticSemanticMatching()

    print(f'Len of {attr1.attr_name}:'.ljust(spacing,' '), f'{len(attr1.lexemes)}')
    print(f'Len of {attr2.attr_name}:'.ljust(spacing,' '), f'{len(attr2.lexemes)}')
    print('')
    print(f'Lex of {attr1.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr1.lexemes]}')
    print(f'Lex of {attr2.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr2.lexemes]}')
    print('')
    sim = helper.getSimilarityOfLexemeLabels(attr1.lexemes, attr2.lexemes)
    print(f'Sim of {attr1.attr_name} and {attr2.attr_name}'.ljust(spacing, ' '), f'{round(sim,4)}')

    print('')
    print(datetime.now())

#term
def test_4():
    spacing = 35
    print(datetime.now())
    print('')

    helper = LexicalAnalysisHelper()

    ## generate attr
    attr1 = MlmAttr('term','Root::XCore::String',0)
    attr2 = MlmAttr('term', 'Root::XCore::String',0)

    attr1.automaticSemanticMatching()
    attr2.automaticSemanticMatching()

    print(f'Len of {attr1.attr_name}:'.ljust(spacing,' '), f'{len(attr1.lexemes)}')
    print(f'Len of {attr2.attr_name}:'.ljust(spacing,' '), f'{len(attr2.lexemes)}')
    print('')
    print(f'Lex of {attr1.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr1.lexemes]}')
    print(f'Lex of {attr2.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr2.lexemes]}')
    print('')
    sim = helper.getSimilarityOfLexemeLabels(attr1.lexemes, attr2.lexemes)
    print(f'Sim of {attr1.attr_name} and {attr2.attr_name}'.ljust(spacing, ' '), f'{round(sim,4)}')

    print('')
    print(datetime.now())

#linktoLSF
def test_5():
    spacing = 35
    print(datetime.now())
    print('')

    helper = LexicalAnalysisHelper()

    ## generate attr
    attr1 = MlmAttr('linkToLSF','Root::XCore::String',0)

    attr1.automaticSemanticMatching()

    print(f'Len of {attr1.attr_name}:'.ljust(spacing,' '), f'{len(attr1.lexemes)}')
    print('')
    print(f'Lex of {attr1.attr_name}:'.ljust(spacing,' '), f'{[l for l in attr1.lexemes]}')

    print('')
    print(datetime.now())

#monograph/book
def test_6():

    helper = LexicalAnalysisHelper()
    helper_wikidata = LexicalAnalysisHelperWikidata()
    helper_babelnet = LexicalAnalysisHelperBabelnet()

    spacing = 60
    print(datetime.now())
    print('')

    class_1 = MlmObject('Root::Model::Monograph', 'Monograph', 1, None, 'false')
    class_2 = MlmObject('Root::Model::Book', 'Book', 1, None, 'false')

    class_1.automaticSemanticMatching()
    class_2.automaticSemanticMatching()

    print(f'Len of {class_1.name}:'.ljust(spacing,' '), f'{len(class_1.lexemes)}')
    print(f'Lex of {class_1.name}:'.ljust(spacing,' '), f'{[l for l in class_1.lexemes]}')
    print('')
    print(f'Len of {class_2.name}:'.ljust(spacing,' '), f'{len(class_2.lexemes)}')
    print(f'Lex of {class_2.name}:'.ljust(spacing,' '), f'{[l for l in class_2.lexemes]}')
    print('')
    print(f'Common Hypernyms of {class_1.name} and {class_2.name}: '.ljust(spacing,' '), f'{[hyp for hyp in helper.getCommonHypernyms(class_1, class_2)]}')

    # print hypernyms of class label
    """
    for l in class_1.lexemes:
        if l[1] == LexicalSources.WORDNET:
            syn = l[0]
            print(f'Synset: {syn}: '.ljust(spacing, ' '), f'{[h for h in syn.hypernyms()]}')
        if l[1] == LexicalSources.WIKIDATA:
            hypernyms = helper_wikidata.getIsSubclassOfEntity(l[0])
            print(f'Synset: {l[0]}: '.ljust(spacing, ' '), f'{[helper_wikidata.getNameofEntity(h) for h in hypernyms]}')
        if l[1] == LexicalSources.BABELNET:
            hypernyms = helper_babelnet._getHypernyms(l[0])
            print(f'Synset: {l[0]}: '.ljust(spacing, ' '), f'{[h for h in hypernyms]}')
    """
                  

def test_7():
    spacing = 40
    print(datetime.now())
    print('')

    helper = LexicalAnalysisHelper()

    attr = ['computeraided', 'durationInMinutes', 'isUngraded', 'maxPoints', 'mustBeRegistered', 'readingTimeInMinutes', 'term']
    attr_b = ['term', 'timeOfExam', 'registrationRequired', 'preparationTimeInMinutes', 'notGraded', 'lengthInMinutes', 'highestScore', 'dateOfExam']

    workbook = xlsxwriter.Workbook('output.xlsx')
    worksheet = workbook.add_worksheet()
    output_file = 'output.xlsx'
    row = 0




    ## generate attr
    for a in attr:
        for b in attr_b:
            row += 1
            attr1 = MlmAttr(a, 'Root::XCore::String',0)
            attr2 = MlmAttr(b, 'Root::XCore::String',0)



            attr1.automaticSemanticMatching()
            attr2.automaticSemanticMatching()

            worksheet.write(row,0,attr1.attr_name)
            worksheet.write(row,1,attr2.attr_name)
            

            sim = helper.getSimilarityOfLexemeLabels(attr1.lexemes, attr2.lexemes)
            worksheet.write(row,2,sim)
            print(f'LexemSim of {attr1.attr_name} and {attr2.attr_name}'.ljust(spacing, ' '), f'{round(sim,4)}')
            sim = helper.getSimilarityOfLabels(attr1.attr_name, attr2.attr_name)
            worksheet.write(row,3,sim)
            print(f'LabelSim of {attr1.attr_name} and {attr2.attr_name}'.ljust(spacing, ' '), f'{round(sim,4)}')
            print('')
            


        print(datetime.now())

    
    workbook.close()



#test_2()

"""
import babelnet as bn
from babelnet.data.relation import BabelPointer
from babelnet.language import Language


a = bn.get_synsets('Course', from_langs=[Language.EN])

a.sort(key=lambda x: len(x.outgoing_edges()), reverse=True)

main_find = a[1]

hyp = main_find.outgoing_edges(BabelPointer.ATTRIBUTE)

for h in hyp: 
    by = bn.get_synset(h.id_target)
    main_sense = by.main_sense(language=Language.EN)
    print(main_sense)
"""


"""
test1: graded/ungraded
test2: highestScore
test3: lengthInMinutes
test4: term
test5: linkToLSF
test6: monograph/book

"""

test_4()