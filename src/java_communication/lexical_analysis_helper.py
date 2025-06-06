# bundles the functions for all sources together
from datetime import datetime
from enum import Enum
import requests as re



try:
    import babelnet as bn
    from babelnet import POS
except:
    # error occurs if babelnet api limit is reached
    pass


from nltk.corpus import wordnet as wn
from wikidata.client import Client as wikidata_client
import spacy

try:
        import babelnet as bn
        from babelnet.language import Language              # Language in which babelnet shall search
        from babelnet.resources import BabelSynsetID        # sometimes the id of a synset is required
        from babelnet.pos import POS as babelPOS            # descriptor whether a noun, verb or other is searched for
        from babelnet.data.source import BabelSenseSource   # allows for restricting sources, where babelnet searches
        from babelnet.data.relation import BabelPointer     # specifies different types fof relations between synsets
except:
    # Do nothing, the import of babelnet fails if the requests limit has been reached in this case we cannot use babelnet anymore. However, since it still tries to import it, it will fail and lead to a faulty state. Best Case just to ignore this, for now. Maybe think about a more sophisticated solution later. 
    print('Babelnet has a limit of 1.000 Requests per day. This limit has been reached')
    pass

API_KEY_MERRIAM = '7d510159-8e29-49a0-b42c-cb4167cbfcd9'

# defines the lexical sources to be added after each return value to increase understandability
class LexicalSources(Enum):
    WORDNET = 'WORDNET'
    BABELNET = 'BABELNET'
    WIKIDATA = 'WIKIDATA'
    MERRIAMWEBSTER = 'MERRIAMWEBSTER'
    CONCEPTNET = 'CONCEPTNET'
    

# bundles the functions for ALL lexial sources
class LexicalAnalysisHelper():

    def performAnalysis_GA(self, model, arg):

        

        
        """
        #print(o1.name)
        #print(o2.name)
        #print(datetime.now())
        c = self.getCommonHypernyms(o1, o2)
        c = self._reduceSetOfHypernyms(c)
        cstr = f'{o1.name} and {o2.name}'
        print(cstr.ljust(50,' '), [a[0] for a in c])
        """

        return ''

    
    def list_intersection(l1: list, l2: list) -> list:
        l3 = [value for value in l1 if value in l2]
        return l3

    def lookForLexeme(self, input: str) -> list:
        lexemeList = []
        listWordnet = LexicalAnalysisHelperWordnet.lookForLexeme(input)
        listWikidata = LexicalAnalysisHelperWikidata.lookForLexeme(input)
        try:
            listBabelnet = LexicalAnalysisHelperBabelnet.lookForLexeme(input)
        except:
            # standard babelnet request limit error
            listBabelnet  = []
        listMerriam = LexicalAnalysisHelperMerriamWebster.lookForLexeme(input)

        for element in listWordnet:
            lexemeList.append(element)

        for element in listWikidata:
            lexemeList.append(element)

        for element in listBabelnet:
            lexemeList.append(element)

        for element in listMerriam:
            lexemeList.append(element)

        return lexemeList
        
    def performTokenization(self, label: str) -> list:
        compunds = []
        j = 0

        for i, char in enumerate(label):
            if char.isupper():
                if i == 0:
                    # compund part doesnt end here
                    continue
                else:
                    if label[i-1].isupper():
                        # compound part is an acronym
                        continue
                    else:
                        # normal compund part
                        compunds.append(label[j:i])
                        j = i

        # add last compund part
        compunds.append(label[j:len(label)])

        return compunds    
    
    def identifyHeadOfCompund(self, compund: str) -> str:
        c = self.performTokenization(compund)
        return c[-1]
    
    def selectRelevantLexemes(listLexemes: list) -> list:
        relevantLexemes = []
        
        # reduce list to nouns
        for element in listLexemes:
            if element[1] == LexicalSources.BABELNET:
                if element[0].pos == babelPOS.NOUN:
                    relevantLexemes.append(element)
                continue

            elif element[1] == LexicalSources.WORDNET:
                if element[0].pos() == 'n':
                    relevantLexemes.append(element)
                continue

                
            elif element[1] == LexicalSources.WIKIDATA:
                pass

            elif element[1] == LexicalSources.MERRIAMWEBSTER:
                if LexicalAnalysisHelperMerriamWebster.checkForNoun(element[0]):
                    relevantLexemes.append(element)
                continue

            elif element[1] == LexicalSources.CONCEPTNET:
                pass

    # TODO reduce the number of hypernyms
    def _reduceSetOfHypernyms(self, hypernyms):
        max_depth_wordnet = -1
        hyp_wordnet = ''
        hypernymsCleaned = []

        for h in hypernyms:
             if h[1] == LexicalSources.WORDNET:
                 ## atm return of the lowest level noun
                 s = h[0]
                 if s.max_depth() > max_depth_wordnet and s.pos() == 'n':
                    hyp_wordnet = h
                    max_depth_wordnet = s.max_depth()

             if h[1] == LexicalSources.BABELNET:
                 pass
             if h[1] == LexicalSources.WIKIDATA:
                 hypernymsCleaned.append(h)
             if h[1] == LexicalSources.MERRIAMWEBSTER:
                pass
             if h[1] == LexicalSources.CONCEPTNET:
                pass
             
        hypernymsCleaned = []
        if hyp_wordnet != '':
            hypernymsCleaned.append(hyp_wordnet)
        return hypernymsCleaned    

    def getCommonHypernyms(self, objectA, objectB) -> list:
        commonHypernyms = []

        lexemesA = objectA.lexemes
        lexemesB = objectB.lexemes

        print(f'Comparision of Lexemes from {objectA.name}: {len(lexemesA)} and {objectB.name}: {len(lexemesB)} ')
        for lexA in lexemesA:
            for lexB in lexemesB:
                # check if source of lexemes is the same
                if lexA[1] == lexB[1]:

                    # act depending on type
                    if lexA[1] == LexicalSources.WORDNET:
                        synA = lexA[0]
                        synB = lexB[0]

                        hyp = synA.lowest_common_hypernyms(synB)
                        for h in hyp:
                            hypernym = (h, LexicalSources.WORDNET)
                            commonHypernyms.append(hypernym)

                    if lexA[1] == LexicalSources.BABELNET:
                        try:
                            hyp = LexicalAnalysisHelperBabelnet.compareHypernmys(LexicalAnalysisHelperBabelnet, lexA[0], lexB[0])
                            for h in hyp:
                                hypernym = (h, LexicalSources.BABELNET)
                                commonHypernyms.append(h)
                        except:
                            # babelnet has a limited number of requests, if that is reached it will return an error, this is just to catch it, idk if we want to do anything special here
                            pass

                    if lexA[1] == LexicalSources.WIKIDATA:

                        hyps = LexicalAnalysisHelperWikidata.compareHypernyms(LexicalAnalysisHelperWikidata(), lexA[0], lexB[0])
                        for h in hyps:
                            commonHypernyms.append(h)

                    # Merriam Webster has no concept of hypernyms
                    if lexA[1] == LexicalSources.MERRIAMWEBSTER:
                        pass
                    
                    # TODO
                    if lexA[1] == LexicalSources.CONCEPTNET:
                        pass

                else:
                    # if source is not the same, no hypernyms can be found (??)
                    pass
            
        # TODO delete duplicates
        return commonHypernyms

    # returns a suited data type of two given data types, returns None if no type fits
    def getCompabilityOfTypes(self, dataTypeA: str, dataTypeB: str) -> str:
        # if they are the same it fits
        if dataTypeA==dataTypeB:
            return dataTypeA
        
        # dont match
        if (dataTypeA == 'Boolean' and dataTypeB == 'Integer') or (dataTypeA == 'Integer' and dataTypeB == 'Boolean'):
            return None

        # dont match
        if (dataTypeA == 'Boolean' and dataTypeB == 'Float') or (dataTypeA == 'Float' and dataTypeB == 'Boolean'):
            return None
        
        # dont match
        if (dataTypeA == 'Boolean' and dataTypeB == 'Date') or (dataTypeA == 'Date' and dataTypeB == 'Boolean'):
            return None

        # dont match
        if (dataTypeA == 'Integer' and dataTypeB == 'Date') or (dataTypeA == 'Date' and dataTypeB == 'Integer'):
            return None
        
        # dont match
        if (dataTypeA == 'Float' and dataTypeB == 'Date') or (dataTypeA == 'Date' and dataTypeB == 'Float'):
            return None

        # float and integer merge to float
        if (dataTypeA == 'Float' and dataTypeB == 'Integer') or (dataTypeB == 'Float' and dataTypeA == 'Integer'):
            return 'Float'
        
        # as the most "basic" type, string can always be used
        # attention!!! the XModeler itself does not do an automatical conversion
        if dataTypeA == 'String' or dataTypeB == 'String':
            return 'String'

    # similiarity of two labels, currently between 0 and 1, we want to change to a different one
    def getSimilarityOfLabels(self, labelA: str, labelB: str) -> float:

        nlp = spacy.load('en_core_web_md')
        tokenA = nlp(labelA)
        tokenB = nlp(labelB)
        return tokenA.similarity(tokenB)

    def getSimilarityOfLexemeLabels(self, listA: list, listB: list) -> list:
        simSum = 0.0
        i = 0
        nlp = spacy.load('en_core_web_md')

        helper = LexicalAnalysisHelper()
        helperWikidata = LexicalAnalysisHelperWikidata()

        for eleA in listA:
            labelA = ""
            if eleA[1] == LexicalSources.WORDNET:
                labelA = eleA[0].name()
                labelA = labelA.split(".")[0]
            elif eleA[1] == LexicalSources.BABELNET:
                try:
                    labelA = str(eleA[0].main_sense()).split(":")[2]
                except:
                    # babelnet has been running out of valid api calls
                    pass
            elif eleA[1] == LexicalSources.WIKIDATA:
                labelA = helperWikidata.getNameofEntity(eleA[0])
            elif eleA[1] == LexicalSources.CONCEPTNET:
                print("label is part of conceptnet")
            elif eleA[1] == LexicalSources.MERRIAMWEBSTER:
                labelA = eleA[0]
            else:
                print("label is part of nothing???", str(eleA[1]))

            tokenA = nlp(labelA)

            if not tokenA.has_vector:
                # TODO wie damit umgehen wenn der token leer ist???
                tkns = helper.performTokenization(labelA)
                newlabel = ' '.join(tkns)
                tokenA = nlp(newlabel)
            

            for eleB in listB:
                labelB = ""
                if eleB[1] == LexicalSources.WORDNET:
                    labelB = eleB[0].name()
                    labelB = labelB.split(".")[0]
                elif eleB[1] == LexicalSources.BABELNET:
                    try:
                        labelB = str(eleB[0].main_sense()).split(":")[2]
                    except:
                         # babelnet has been running out of valid api calls
                        pass
                elif eleB[1] == LexicalSources.WIKIDATA:
                    labelB = helperWikidata.getNameofEntity(eleB[0])
                    # TODO REMOVE THIS, but right now we need him to be removed
                    if "Lord Summerisle" in str(labelB):
                        continue
                elif eleB[1] == LexicalSources.CONCEPTNET:
                    print("label is part of conceptnet")
                elif eleB[1] == LexicalSources.MERRIAMWEBSTER:
                    labelB = eleB[0]
                else:
                    print("label is part of nothing???", str(eleA[1]))

                i+=1


                
                tokenB = nlp(labelB)

                if not tokenB.has_vector:
                    # TODO wie damit umgehen wenn der token leer ist???
                    tkns = helper.performTokenization(labelB)
                    newlabel = ' '.join(tkns)
                    tokenB = nlp(newlabel)
                

                
                simSum+= tokenA.similarity(tokenB)

        try:
            avg = simSum / i
        except: # float division by zero
            avg = 0.0
        return avg


# bundles the functions for wordnet
class LexicalAnalysisHelperWordnet():
    
    def lookForLexeme(input: str) -> list:
        syns = wn.synsets(input)
        lexemeList = []

        for syn in syns:
            lexemeList.append((syn, LexicalSources.WORDNET))
        
        return lexemeList


# bundles the functions for babelnet
class LexicalAnalysisHelperBabelnet():
    
    def lookForLexeme(input: str) -> list:
        lexemeList = []
        # reduction to nouns to increase performance
        syns = bn.get_synsets(input, from_langs=[Language.EN], poses=[POS.NOUN])
        for syn in syns:
            lexemeList.append((syn, LexicalSources.BABELNET))
        return lexemeList

    # compare hypernyms from babelnet based on babelnet synsets
    def compareHypernmys(self, synset1, synset2):

        l1 = self._getHypernyms(synset1)
        l2 = self._getHypernyms(synset2)

        list_of_common_hyps = LexicalAnalysisHelper.list_intersection(l1, l2)
        list_of_common_hyps = list(dict.fromkeys(list_of_common_hyps))

        return list_of_common_hyps


        # gets hypernyms of a synset in babelnet
    
    def _getHypernyms(synset):
        hypernyms = []
        for edge in synset.outgoing_edges(BabelPointer.ANY_HYPERNYM):
            # synset das hypernym ist
            by = bn.get_synset(edge.id_target)
            # main sense / meaning for this synset
            main_sense = by.main_sense(language=Language.EN)
            
            hypernyms.append(main_sense)    

        return hypernyms

# bundles the functions for wikidata
class LexicalAnalysisHelperWikidata():

    def lookForLexeme(input: str) -> list:
        client = wikidata_client()
        listLexemes = []

        params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': input,
        'language': 'en'
        }

        url = 'https://www.wikidata.org/w/api.php'
        data = re.get(url, params=params)   
        data = data.json()

        ids = data['search']

        for id in ids:
            entity = client.get(id['id'])
            listLexemes.append((entity,LexicalSources.WIKIDATA))
        
        return listLexemes
    
    # generic function to return the entities of a entity under consideration a specific property
    def _getPropertyValues(self, entity, property):
        a = []

        try:
            instances = entity.attributes['claims'][property]
        except:
            return []
        
        for instance in instances:
            id = instance['mainsnak']['datavalue']['value']['id']
            entity = self._getEntity(id)
            a.append(entity)
        return a

    # returns the entities of the wikidata page with the property "Instances of"
    def getIsInstancesOfEntity(self, entity):
        return self._getPropertyValues(entity, property='P31')

    # returns a wikidata page
    def _getEntity(self, word: str):

        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'search': word,
            'language': 'en'
        }

        url = 'https://www.wikidata.org/w/api.php'
        data = re.get(url, params=params)

        data = data.json()
        
        # we always take the first results at the moment, as this is the most likely one to be correct (?)
        id = data['search'][0]['id']

        client = wikidata_client()
        entity = client.get(id)
        
        return entity

    # returns the entities of the wikidata page with the property "Subclass of"
    def getIsSubclassOfEntity(self, entity):
        return self._getPropertyValues(entity=entity, property='P279')

    # returns the name of a wikidata page
    def getNameofEntity(self, entity):
        return entity.attributes['labels']['en']['value']

    # returns the id of an entitity, used for comparing two entities
    def getIDOfEntity(self, entity):
        return entity.attributes['title']

    def compareHypernyms(self, entityA, entityB) -> list:


        listHypernyms = []

        subclassesA = self.getIsSubclassOfEntity(entity=entityA)
        subclassesB = self.getIsSubclassOfEntity(entity=entityB)

        for subA in subclassesA:
            for subB in subclassesB:
                if self.getIDOfEntity(subA) == self.getIDOfEntity(subB):
                    hypernym = (subA, LexicalSources.WIKIDATA)
                    listHypernyms.append(hypernym)

        return listHypernyms


# bundles the functions for merriam webster
class LexicalAnalysisHelperMerriamWebster():
    
    def lookForLexeme(input: str) -> list:
        URL_merriam = f'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{input}?key={API_KEY_MERRIAM}'

        listLexemes = []

        response = re.get(URL_merriam)
        if response.status_code == 200:
            data = response.json()
            try:
                data = data[0]['meta']['id']
                listLexemes.append((data, LexicalSources.MERRIAMWEBSTER))
            except:
                # no lexeme found, spelling mistakes come later
                pass

        return listLexemes

    def checkForNoun(input: str) -> bool:

        URL_merriam = f'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{input}?key={API_KEY_MERRIAM}'

        response = re.get(URL_merriam)
        if response.status_code == 200:
            try:
                data = response.json()
                data = data[0]['fl']
                return data == 'noun'
            except:
                return False
        return False


# bundles the functions for concept net
class LexicalAnalysisHelperConceptNet():
    pass


