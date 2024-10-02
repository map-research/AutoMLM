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
        self.maxWordSenses = int(maxWordSenses) 
        self.depthTopLevel =  int(depthTopLevel)
        self.acceptingValueSim = float(acceptingValueSim)
        self.rejectingValueSim = float(rejectingValueSim)
        self.helper = LexicalAnalysisHelper()


    def perform_Analysis(self) -> str:
        if self.promotionCategory =='GA':
            path = self.perform_GA()
        return path
        


    def perform_GA(self) -> str:
        # create new model
        # random id generation to allow for multiple openings of the "same" diagram

        acceptingValueSim = self.acceptingValueSim

        id = randint(0,5000)
        modelName = 'Root::Modell' + str(id)
        new_Model = xml_export.preamble(modelName)
        projectName = new_Model.attrib['path']

        objects = self.model.mlm_objects

        # combination of every two indexes, only once
        numbers = list(range(len(objects)))
        combis = combinations(numbers, 2)

        # find hypernym for every combination of classes
        for combi in combis:
                    
            genCand = []
            o1 = objects[combi[0]]
            o2 = objects[combi[1]]

            hypernyms = self.helper.getCommonHypernyms(o1,o2)

            print("")
            cstr = f'{o1.name} and {o2.name}'
            print(cstr.ljust(50,' '), [a for a in hypernyms])

            # compare attribitues
            for attr_a in o1.attr_list:
                for attr_b in o2.attr_list:

                    sim = self.helper.getSimilarityOfLexemeLabels(attr_a.lexemes, attr_b.lexemes)


                    type = self.helper.getCompabilityOfTypes(attr_a.attr_type, attr_b.attr_type)

                    cstr = f'{attr_a.attr_name} & {attr_b.attr_name}'
                    if sim > acceptingValueSim:
                        genCand.append(GeneralisationCandiate(o1, o2, attr_a, attr_b, sim, type, hypernyms))
                        print(cstr.ljust(50,' '), f'{round(sim,4)} is {type}')




        # TODO check ob für 2 klassen ein attribut mit mehr als einem anderen gemergt werden kann / soll. Falls ja entferne die jenigen mit dem geringsten sim wert


        # create parent class and give attributes

        # TODO do a sensible approach when to generalize
        if True:

            class_name = "Class_A"
            parentCl = MlmObject(projectName+"::"+class_name, class_name, 1, None, False)


            genCand.sort(key=lambda x: x.sim, reverse=True)
            attsToBeGeneralized = []


            for entry in genCand:
                if entry.type == None:
                    type = "Root::XCore::String"
                else:
                    type = entry.type

                if entry.a1.attr_name in attsToBeGeneralized:
                    continue
                else:
                    attsToBeGeneralized.append(entry.a1.attr_name)
                    attsToBeGeneralized.append(entry.a2.attr_name)

            # TODO how to decide for an attr name?
                name = entry.a1.attr_name

                parentCl.add_attr(MlmAttr(name, type, 0))

            parentCl.export(new_Model)
            
            for o in objects:
                cl =  MlmObject(projectName+"::"+o.name, o.name, 1, None, False)
                for attr in o.attr_list:
                    if attr.attr_name in attsToBeGeneralized:
                        continue
                    attr = MlmAttr(attr.attr_name, attr.attr_type, 0)
                    cl.add_attr(attr)
                cl.add_parent_class(parentCl)
                cl.export(new_Model)

            xml_export.writeXML(new_Model, 'C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\output.xml')

            return 'C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\output.xml'

class GeneralisationCandiate:
    def __init__(self, o1: MlmObject, o2: MlmObject, a1: MlmAttr, a2: MlmAttr, sim: float, type: str, hypernyms: list):
        self.o1 = o1
        self.o2 = o2
        self.a1 = a1
        self.a2 = a2
        self.sim = sim
        self.type = type
        self.hypernyms = hypernyms