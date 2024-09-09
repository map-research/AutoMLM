## all lexical analysis have to be here to avoid circular imports



from itertools import combinations
from mlm_helper_classes import MlmAttr, MlmObject
from lexical_analysis_helper import LexicalAnalysisHelper
import xml_export
from mlm_class import MultilevelModel
from random import randint


class LexicalAnalysis:

    def __init__(self, model: MultilevelModel, promotionCategory: str, maxWordSenses: int, depthTopLevel: int, acceptingValueSim: float,  rejectingValueSim: float) -> None:

        self.model = model
        self.promotionCategory = promotionCategory
        self.maxWordSenses = maxWordSenses 
        self.depthTopLevel =  depthTopLevel
        self.acceptingValueSim = acceptingValueSim
        self.rejectingValueSim = rejectingValueSim
        self.helper = LexicalAnalysisHelper()


    def perform_Analysis(self) -> str:
        if self.promotionCategory =='GA':
            path = self.perform_GA()
        return path
        


    def perform_GA(self) -> str:
        # create new model
        # random id generation to allow for multiple openings of the "same" diagram

        id = randint(0,5000)
        modelName = 'Root::Modell' + str(id)
        new_Model = xml_export.preamble(modelName)
        projectName = new_Model.attrib['path']

        objects = self.model.mlm_objects

        readable_hypernyms = set()


        # combination of every two indexes, only once
        numbers = list(range(len(objects)))
        combis = combinations(numbers, 2)

        # find hypernym for every combination of classes
        for combi in combis:
                    
            o1 = objects[combi[0]]
            o2 = objects[combi[1]]

            hypernyms = self.helper.getCommonHypernyms(o1,o2)

            cstr = f'{o1.name} and {o2.name}'
            print(cstr.ljust(50,' '), [a[0] for a in hypernyms])



            #readable_hypernyms.add([a[0] for a in hypernyms])
            print(readable_hypernyms)


        # create new model with "old" aspects
        for o in objects:
            cl =  MlmObject(projectName+"::"+o.name, o.name, 1, None, False)
            for attr in o.attr_list:
                attr = MlmAttr(attr.attr_name, attr.attr_type, 0)
                cl.add_attr(attr)
            cl.export(new_Model)

        pathNew = 'AutoMLM\\mlm_files\\deepModel.xml'
        xml_export.writeXML(new_Model, pathNew)
        return pathNew
        


