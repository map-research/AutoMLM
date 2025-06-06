# this class bundles all the functions needed to communicate with the different lexicons and their apis
import nltk
from nltk.corpus import wordnet as wn

from enum import Enum
import requests as re

from wikidata.client import Client as wikidata_client


try:
    import babelnet as bn
    from babelnet.language import Language              # Language in which babelnet shall search
    from babelnet.resources import BabelSynsetID        # sometimes the id of a synset is required
    from babelnet.pos import POS                        # descriptor whether a noun, verb or other is searched for
    from babelnet.data.source import BabelSenseSource   # allows for restricting sources, where babelnet searches
    from babelnet.data.relation import BabelPointer     # specifies different types fof relations between synsets
except:
    # Do nothing, the import of babelnet fails if the requests limit has been reached ...
    # in this case we cannot use babelnet anymore. However, since it still tries to import it,
    # it will fail and lead to a faulty state. Best Case just to ignore this, for now.
    # Maybe think about a more sophisticated solution later. 
    pass



# API Key for merriam webster dict, should not be here but somewhere safe
API_KEY_MERRIAM = '7d510159-8e29-49a0-b42c-cb4167cbfcd9'


class WordTpyes_Wordnet(Enum):
    ALL = 0 # alle Worttypen
    NOUN = wn.NOUN
    ADJ = wn.ADJ
    VERB = wn.VERB


# returns synonyms as set
# returns all synsets for one lexeme
def getSynonyms_wordnet(lexeme: str) -> set:
    listSynonyms = wn.synonyms(lexeme)
    setSynonyms = set()
    for liste in listSynonyms:
        for word in liste:
            setSynonyms.add(word)
    return setSynonyms


# returns the lemmas as string set
def getLemmas_wordnet(lexeme: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, isLemmaOwner: bool = True) -> set:
    setLemmas = set()
    if type == WordTpyes_Wordnet.ALL:
        senses = wn.synsets(lexeme)
    else:
        senses = wn.synsets(lexeme, type.value)

    if isLemmaOwner:
        senses = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(lexeme, x), senses))

    for syn in senses:
        for lemma in wn.synset(syn.name()).lemmas():
            setLemmas.add(lemma.name())
    return setLemmas


# returns the lemmas of a sense
def getLemmasBySense_wordnet(sense) -> set:
    setLemmas = set()
    for lemma in sense.lemmas():
        setLemmas.add(lemma.name())
    return setLemmas


# returns hypernyms of a word lexeme as set of lemmas
def getHypernyms_wordnet(lexeme: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, isLemmaOwner: bool = True) -> set:
    sethypernyms = set()
    if type == WordTpyes_Wordnet.ALL:
        senses = wn.synsets(lexeme)
    else:
        senses = wn.synsets(lexeme, type.value)

    if isLemmaOwner:
        senses = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(lexeme, x), senses))

    for sense in senses:
        for hypernym in sense.hypernyms():
            for lemma in wn.synset(hypernym.name()).lemmas():
                sethypernyms.add(lemma.name())
    return sethypernyms

# returns hypernyms of a lemma
def getHypernyms_wordnet(lemma: str) -> set:
    # hypernyms are of a word sense to which the lemma belongs
    sethypernyms = set()
    sense = wn.synset(lemma)
    for hypernym in sense.hypernyms():
        for lemma in wn.synset(hypernym.name()).lemmas():
            sethypernyms.add(lemma.name())
    return sethypernyms


# get hyponyms as a set of lemmas
def getLemmaOfHyponyms_wordnet(lexeme: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, isLemmaOwner: bool = True) -> set:
    setHyponyms = set()
    if type == WordTpyes_Wordnet.ALL:
        senses = wn.synsets(lexeme)
    else:
        senses = wn.synsets(lexeme, type.value)

    if isLemmaOwner:
        senses = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(lexeme, x), senses))

    for sense in senses:
        for hypernym in sense.hyponyms():
            for lemma in wn.synset(hypernym.name()).lemmas():
                setHyponyms.add(lemma.name())
    return setHyponyms


# get the lemma of the root hypernym
def getLemmaOfRootHypernyms_wordnet(lexeme: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, isLemmaOwner: bool = True) -> set:
    setRootHypernyms = set()
    if type == WordTpyes_Wordnet.ALL:
        senses = wn.synsets(lexeme)
    else:
        senses = wn.synsets(lexeme, type.value)

    if isLemmaOwner:
        senses = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(lexeme, x), senses))

    for sense in senses:
        for hypernyms in sense.root_hypernyms():
            for lemma in wn.synset(hypernyms.name()).lemmas():
                setRootHypernyms.add(lemma.name())
    return setRootHypernyms


"""
# returns lemmas of the lowest common hypernym and its depth
def getLowestCommonhypernym_wordnet(term1: str, term2: str, type1: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, type2: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, onlyOwnersOfSynset: bool = True) :
    commonHypernym = [set(),]
    if type1 == WordTpyes_Wordnet.ALL:
        synsets1 = wn.synsets(term1)
    else:
        synsets1 = wn.synsets(term1, type1.value)

    if type2 == WordTpyes_Wordnet.ALL:
        synsets2 = wn.synsets(term2)
    else:
        synsets2 = wn.synsets(term2, type2.value)

    if onlyOwnersOfSynset:
        synsets1 = list(filter(lambda x: isSynsetOwnerTerm_wordnet(term1, x), synsets1))
        synsets2 = list(filter(lambda x: isSynsetOwnerTerm_wordnet(term2, x), synsets2))

    high = 0

    for syn1 in synsets1:
        for syn2 in synsets2:
            for common in wn.synset(syn1.name()).lowest_common_hypernyms(wn.synset(syn2.name())):
                    # find highest common synonym
                    n = getDepthLemma_wordnet(common)
                    if n >= high:
                        highestSyn = common
                        high = n

    # add lemmas of highest common synonym            
    for lemma in getLemmasBySynset_wordnet(highestSyn):
        commonHypernym[0].add(lemma)
    commonHypernym.append(n)

    return commonHypernym
"""

# returns the owner lemma of the lowest common hypernym of two lemmas
def getLowestCommonHypernym_wordnet(lemma1 : str, lemma2: str):
    # senses have hypernyms, therefore get the sense of the lemmas
    l1 = wn.synset(lemma1)
    l2 = wn.synset(lemma2)

    # get the sense of the lowest hypernym
    commonHypernym = l1.lowest_common_hypernyms(l2)
    return commonHypernym[0]

# get antonyms of term as set of lemmas
def getAntonyms_wordnet(lexeme: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> set:
    pass


# returns a set of lemmas pertainyms (belongs-to, relationships) of the term
def getPertainyms_wordnet(lexeme: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, isLemmaOwner: bool = True) -> set:
    #lemma.pertainyms()
    setPertainyms = set()
    if type == WordTpyes_Wordnet.ALL:
        senses = wn.synsets(lexeme)
    else:
        senses = wn.synsets(lexeme, type.value)

    if isLemmaOwner:
        senses = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(lexeme, x), senses))

    for sense in senses:
        for lemma in wn.synset(sense.name()).lemmas():
            for lemma1 in lemma.pertainyms():
               setPertainyms.add(lemma1.name())
    

    if len(setPertainyms) > 0:
        return setPertainyms
    else:
        return set()
    

# returns Leacock-Chodorow similarity based on the shortest based on the shortest path that connects the senses (as above) and the maximum depth of the taxonomy
def getLeaChoSimilarity_wordnet(term1: str, term2: str, type1: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, type2: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, isLemmaOwner:bool = True) -> list:
    similarites = []
    if type1 == WordTpyes_Wordnet.ALL:
        senses1 = wn.synsets(term1)
    else:
        senses1 = wn.synsets(term1, type1.value)

    if type2 == WordTpyes_Wordnet.ALL:
        senses2 = wn.synsets(term2)
    else:
        senses2 = wn.synsets(term2, type2.value)

    if isLemmaOwner:
        senses1 = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(term1, x), senses1))
        senses2 = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(term2, x), senses2))

    for sense1 in senses1:
        for sense2 in senses2:
            try:
                similarites.append(round(wn.lch_similarity(sense1, sense2),2))
            except:
                # error occurs when different types are compared, for the moment just skip
                pass
    # sort list descending
    similarites.sort(reverse=True)
    return similarites


# returns similarity based on the shortest hypernym path for every pair of senses
def getPathSimilarity_wordnet(lexeme1: str, lexeme2: str, type1: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, type2: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, isLemmaOwner: bool=True) -> list:
    similarites = []
    if type1 == WordTpyes_Wordnet.ALL:
        senses1 = wn.synsets(lexeme1)
    else:
        senses1 = wn.synsets(lexeme1, type1.value)

    if type2 == WordTpyes_Wordnet.ALL:
        senses2 = wn.synsets(lexeme2)
    else:
        senses2 = wn.synsets(lexeme2, type2.value)

    if isLemmaOwner:
        senses1 = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(lexeme1, x), senses1))
        senses2 = list(filter(lambda x: isLemmaOwnerOfWordSense_wordnet(lexeme2, x), senses2))


    for sense1 in senses1:
        for sense2 in senses2:
            #similarites.append(str(syn1) + " " + str(syn2) + " " + str(round(wn.path_similarity(syn1, syn2),2)))
            similarites.append(round(wn.path_similarity(sense1, sense2),2))
    # sort list descending
    similarites.sort(reverse=True)
    return similarites


# return a boolean of whether two terms are synonyms of each other
def areSynonyms_wordnet(lexeme1: str, lexeme2: str) -> bool:
    lexeme1 = lexeme1.lower()
    lexeme2 = lexeme2.lower()
    senses = getSynonyms_wordnet(lexeme1)
    return lexeme2 in senses


# returns the owner lemma of a sense as a string
def getOwnerofLemma_wordnet(sense: nltk.corpus.reader.wordnet.Synset) -> str:
    return sense.name().split(".")[0]


# returns whether the owner of the sense is the lexeme
def isLemmaOwnerOfWordSense_wordnet(lexeme: str, syn: nltk.corpus.reader.wordnet.Synset) -> bool:
    a = getOwnerofLemma_wordnet(syn)
    return a.lower()==lexeme.lower()


def getDepthLemma_wordnet(lemma : str, fake_root : bool = True) -> int:
    l1 = wn.synset('Cat.n.01')
    path = l1._shortest_hypernym_paths(True)
    depth = max(path.values())
    return depth


"""
probably no longer needed as the better and real function was discovered
# analyse the rank of a synset, based on the hypernym structure  as multiple paths are possible, all values are returned
def getDepthSynset_wordnet(syn: nltk.corpus.reader.wordnet.Synset,index,depth,ranks=[]):

    # depth is bigger
    depth = depth+1

    # if ranks is empty create a new one; only for initinal use Required
    if len(ranks)==0:
        ranks.append(0)

    # if more than one path we need another index
    if len(ranks) < index+1:
        ranks.append(depth)
    else:
        ranks[index] = depth
    
    # if end of hyps is reached, end 
    if len(syn.hypernyms()) == 0:
        return depth, ranks
    else:
        # if we need to go multiple paths, we need to save the current path
        if len(syn.hypernyms()) > 1:
            d = depth

        # go through all hypernyms, enumerator needed for identification of numbers
        for enumerator in enumerate(syn.hypernyms()):
            # if we are not in the first path we need to switch to the next index and the saved depth
            if enumerator[0] > 0:
                index +=1
                depth = d
            
            # save depth and ranks
            depth, ranks = (getDepthSynset_wordnet(syn.hypernyms()[enumerator[0]],index,depth)[enumerator[0]]), ranks
        return depth, ranks
    

# returns the depth of a synset only - can return an integer or a list of integer if more paths are possible
def getDepthFromSynset_wordnet(syn: nltk.corpus.reader.wordnet.Synset,index=0,depth=0,ranks=[]):
    ranks = getDepthSynset_wordnet(syn,index,depth,ranks)

    # returns the rank, dependent if it is an integer, or a list; if it is a list, only the deepest rank is returned 
    if type(ranks[0]) == int:
        return ranks[0]
    else: 
        high = 0
        for a in ranks[0]:
            if a > high:
                a = high
        return a
"""

def check_wordnet():
    try:
        nltk.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')


# gets hypernyms of a word in babelnet
def getHypernyms_babelnet_word(word: str):
    # TODO abklären ob alle Quellen benutzt werden sollen oder nur manche?
    hypernyms = []
    synsets = bn.get_synsets(word, from_langs=[Language.EN])#, sources=[BabelSenseSource.WIKIDATA])
    
    if len(synsets) == 0:
        # kein lexeme vorhanden
        return hypernyms

    for synset in synsets:
        # ANY_HYPERNYM sucht in allen Quellen nach passenden Hypernymen
        for edge in synset.outgoing_edges(BabelPointer.ANY_HYPERNYM):
            # synset das hypernym ist
            by = bn.get_synset(edge.id_target)
            # main sense / meaning for this synset
            main_sense = by.main_sense(language=Language.EN)
            
            hypernyms.append(main_sense)

    return hypernyms


def getDistance_wordnet(lemma1 : str, lemma2 : str):

    l1 = wn.synset(lemma1)
    l2 = wn.synset(lemma2)

    return l1.shortest_path_distance(l2)








# gets hypernyms of a synset in babelnet
def getHypernyms_babelnet(synset):
    hypernyms = []
    for edge in synset.outgoing_edges(BabelPointer.ANY_HYPERNYM):
        # synset das hypernym ist
        by = bn.get_synset(edge.id_target)
        # main sense / meaning for this synset
        main_sense = by.main_sense(language=Language.EN)
        
        hypernyms.append(main_sense)    

    return hypernyms


# gets all synsets from babelnet
def getSynsets_babelnet(word: str):
    return bn.get_synsets(word, from_langs=[Language.EN])


# get all synsets of word
def getSense_babelnet(word: str):
    
    synsets = bn.get_synsets(word, from_langs=[Language.EN])
    # if no synsets exists, no senses will exist either
    if len(synsets) == 0:
        return []
    
    a = []
    # get all the main senses for every synset
    for by in synsets:
        a.append(by.main_sense(language=Language.EN))
    
    return a


# returns the common entries of two lists
def list_intersection(l1: list, l2: list) -> list:
    l3 = [value for value in l1 if value in l2]
    return l3


# compare hypernyms from babelnet based on words
def compareHypernyms_babelnet_word(w1: str, w2: str) -> set:

    # get the hypernyms 
    l1 = getHypernyms_babelnet_word(w1)
    l2 = getHypernyms_babelnet_word(w2)

    # find common hypernyms and remove duplicates
    list_of_common_hyps = list_intersection(l1, l2)
    list_of_common_hyps = list(dict.fromkeys(list_of_common_hyps))

    return list_of_common_hyps


# compare hypernyms from babelnet based on babelnet synsets
def compareHypernmys_babelnet(synset1, synset2):

    l1 = getHypernyms_babelnet(synset1)
    l2 = getHypernyms_babelnet(synset2)

    list_of_common_hyps = list_intersection(l1, l2)
    list_of_common_hyps = list(dict.fromkeys(list_of_common_hyps))

    return list_of_common_hyps


## TODO find out what BabelPointer.SEMANTICALLY_RELATED is and what other BabelPointer exists and how we can use them, e.g. Synonyms(BabelPointer.SEMANTICALLY_RELATED):
"""
 s1 = bn.get_synset(BabelSynsetID('bn:14292888n'))

    for edge in s1.outgoing_edges(BabelPointer.SEMANTICALLY_RELATED):
        by = bn.get_synset(edge.id_target)
        main_sense = by.main_sense(language=Language.EN)
        print(main_sense)
"""


# returns related words of merriam webster
def getRelatedWords_merriam(word: str) -> set:
    URL_merriam = f'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={API_KEY_MERRIAM}'
    setRelatedWords = set()
    
    response = re.get(URL_merriam)

    if response.status_code==200:   
        data = response.json()
        try:
            relatedWordList = data[0]['def'][0]['sseq'][0][0][1]['rel_list']
            for wordList in relatedWordList:
                for word in wordList:
                    setRelatedWords.add(word.get('wd'))
        except:
            # there are no related words for this sense
            return setRelatedWords

    return setRelatedWords


# returns synonyms of merriam webster
def getSynonyms_merriam(word: str) -> set:
    URL_merriam = f'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={API_KEY_MERRIAM}'
    setSynonyms = set()

    response = re.get(URL_merriam)
    if response.status_code==200:
        data = response.json()

        # it is possible that the answer is positive but the word is a spelling mistake
        # in that case the response is differently formatted, therefore, an empty list is 
        # returned, this can be improved by using the getCorrections_merriam functions to 
        # identify the correct spelling of the word
        try:
            # extracts the synonyms of the different senses
            synonymsSenses = data[0]['meta']['syns']
        except:
            synonymsSenses = []

        for sense in synonymsSenses:
            # get the synonyms of every sense
            for synonym in sense:
                setSynonyms.add(synonym)
    
    return setSynonyms


# returns a number of word stems based on merriam webster dictionary
def getStem_merriam(word: str) -> set:
    URL_merriam = f'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={API_KEY_MERRIAM}'
    setStems = set()

    response = re.get(URL_merriam)

    if response.status_code==200:
        data = response.json()

        # extracts the synonyms of the different senses
        stems = data[0]['meta']['stems']

        for stem in stems:
            setStems.add(stem)
        
    return stems


# if a word is mispelled, merriam webster offers different options to correct the word
def getCorrections_merriam(word: str):
    URL_merriam = f'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={API_KEY_MERRIAM}'
    response = re.get(URL_merriam)
    corrections = []

    # the list is sorted from most likely to less likely options
    if response.status_code==200:
        data = response.json()
        corrections = data
    return corrections


# higher usability for merriam webster, finds synonmys. if the word is mispelled, the first correction
# suggestion will be used
def getSynonymsCorrected_merriam(word: str):
    synonyms = getSynonyms_merriam(word)
    if (len(synonyms))==0:
        corrections = getCorrections_merriam(word)
        synonyms = getSynonyms_merriam(corrections[0])

    return synonyms


# returns a wikidata page
def getWikidataPage(word: str):

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


# returns the name of a wikidata page
def getWikidataNameofPage(entity):
    return entity.attributes['labels']['en']['value']


# generic function to return the entities of a entity under consideration a specific property
def getWikidataPropertyValues(entity, property):
    a = []

    try:
        instances = entity.attributes['claims'][property]
    except:
        return []
    
    for instance in instances:
        id = instance['mainsnak']['datavalue']['value']['id']
        entity = getWikidataPage(id)
        a.append(entity)
    return a


# returns the entities of the wikidata page with the property "Instances of"
def getIsInstancesOfEntity_wikidata(entity):
    return getWikidataPropertyValues(entity, property='P31')


# returns the entities of the wikidata page with the property "Subclass of"
def getIsSubclassOfEntity_wikidata(entity):
    return getWikidataPropertyValues(entity, property='P279')


# returns the entities of the wikidata page with the property "opposite of" (Antonyms)
def getOppositeOfEntity_wikidata(entity):
    return getWikidataPropertyValues(entity, 'P461')


# returns the entities of the wikidata page with the property "Is Said to Be the same" (synonyms but sometimes disputed)
def getIsSaidToBeTheSameAs_wikidata(entity):
    return getWikidataPropertyValues(entity, 'P460')


# returns the entities of the wikidata page with the property "Meta Sub Class of"
def getIsMetaSubClassOf_wikidata(entity):
    return getWikidataPropertyValues(entity, 'P2445')


# returns the entities of the wikidata page with the property "Meta Class For"
def getIsMetaClassFor_wikidata(entity):
    return getWikidataPropertyValues(entity, 'P8225')


# returns the entities of the wikidata page with the property "is Part of"
def getIsPartOf_wikidata(entity):
    return getWikidataPropertyValues(entity, 'P361')


# returns the entities of the wikidata page with the property "has Part"
def hasParts_wikidata(entity):
    return getWikidataPropertyValues(entity, 'P527')


# prints all properties and their "name"
def getAllPropertyDescriptors(entity):
    client = wikidata_client()
    properties = entity.attributes['claims']

    for property in properties:
        print(property, getWikidataNameofPage(client.get(property)))


if __name__ == "__main__":
   
    parts = getIsPartOf_wikidata(getWikidataPage('Room'))
    for part in parts:
        print(getWikidataNameofPage(part))

    

