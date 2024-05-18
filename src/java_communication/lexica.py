# this class bundles all the functions needed to communicate with the different lexicons and their apis

import nltk
from nltk.corpus import wordnet as wn
from enum import Enum


# TODO Discusss whether all types is a suitable standard decision, maybe Noun is more appropiate
# TODO Discuss getLowestCommonHypernym_wordnet -> generelle diskussion wie vorgehen mit der verbindung von synsets zu wörtern
# TODO Discuss getAntonyms_wordnet
# TODO Discuss other similiarites methods and whether they are appropiate and which we don want to use

class WordTpyes_Wordnet(Enum):
    ALL = 0
    NOUN = wn.NOUN
    ADJ = wn.ADJ
    VERB = wn.VERB

# converts a set of synsets to synset names
def convertSysnsetToNames_wordnet(syns: set):
    names = set()
    for syn in syns:
        names.add(syn.name())
    return names


# returns synonyms as set
def getSynonyms_wordnet(term: str) -> set:
    listSynonyms = wn.synonyms(term)
    setSynonyms = set()
    for liste in listSynonyms:
        for word in liste:
            setSynonyms.add(word)
    return setSynonyms


# returns the lemmas as string set
def getLemmas_wordnet(term: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> set:
    setLemmas = set()
    if type == WordTpyes_Wordnet.ALL:
        synsets = wn.synsets(term)
    else:
        synsets = wn.synsets(term, type.value)

    for syn in synsets:
        for lemma in wn.synset(syn.name()).lemmas():
            setLemmas.add(lemma.name())
    return setLemmas


# returns the lemmas of a synset
def getLemmasBySynset_wordnet(syn) -> set:
    setLemmas = set()
    for lemma in syn.lemmas():
        setLemmas.add(lemma.name())
    return setLemmas


# returns hypernyms as set of lemmas
def getHyperonyms_wordnet(term: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> set:
    setHyperonyms = set()
    if type == WordTpyes_Wordnet.ALL:
        synsets = wn.synsets(term)
    else:
        synsets = wn.synsets(term, type.value)

    for syn in synsets:
        for hyp in syn.hypernyms():
            for lemma in wn.synset(hyp.name()).lemmas():
                setHyperonyms.add(lemma.name())
    return setHyperonyms


# get hyponyms as a set of lemmas
def getHyponyms_wordnet(term: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> set:
    setHyponyms = set()
    if type == WordTpyes_Wordnet.ALL:
        synsets = wn.synsets(term)
    else:
        synsets = wn.synsets(term, type.value)

    for syn in synsets:
        for hyp in syn.hyponyms():
            for lemma in wn.synset(hyp.name()).lemmas():
                setHyponyms.add(lemma.name())
    return setHyponyms


# get the lemma of the root hypernym
def getRootHyperonyms_wordnet(term: str, type: WordTpyes_Wordnet.ALL) -> set:
    setRootHypernyms = set()
    if type == WordTpyes_Wordnet.ALL:
        synsets = wn.synsets(term)
    else:
        synsets = wn.synsets(term, type.value)

    for syn in synsets:
        for hyp in syn.root_hypernyms():
            for lemma in wn.synset(hyp.name()).lemmas():
                setRootHypernyms.add(lemma.name())
    return setRootHypernyms


# returns synsets of the lowest common hypernym, curently all synsets of a word a used
def getLowestCommonHyperonym_wordnet(term1: str, term2: str, type1: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, type2: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> set:
    # TODO suche ist zwishen zwei Synsets, da wir aber nur zwei Suchbegriffe haben müssen wir überlegen, 
    # ob wir zwischen Allen Synsets eines Begriffes suchen sollten, oder wie man hier am besten vorgehen kann
    commonHypernym = set()
    if type1 == WordTpyes_Wordnet.ALL:
        synsets1 = wn.synsets(term1)
    else:
        synsets1 = wn.synsets(term1, type1.value)

    if type2 == WordTpyes_Wordnet.ALL:
        synsets2 = wn.synsets(term2)
    else:
        synsets2 = wn.synsets(term2, type2.value)

    for syn1 in synsets1:
        for syn2 in synsets2:
            for common in wn.synset(syn1.name()).lowest_common_hypernyms(wn.synset(syn2.name())):
                for lemma in getLemmasBySynset_wordnet(common):
                    commonHypernym.add(lemma)

    return commonHypernym


# get antonyms of term as set of lemmas
def getAntonyms_wordnet(term: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> set:
    pass


# returns a set of lemmas pertainyms (belongs-to, relationships) of the term
def getPertainyms_wordnet(term: str, type: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> set:
    #lemma.pertainyms()
    setPertainyms = set()
    if type == WordTpyes_Wordnet.ALL:
        synsets = wn.synsets(term)
    else:
        synsets = wn.synsets(term, type.value)

    for syn in synsets:
        for lemma in wn.synset(syn.name()).lemmas():
            for lemma1 in lemma.pertainyms():
               setPertainyms.add(lemma1.name())
    
    # besser so? oder leeres set?
    if len(setPertainyms) > 0:
        return setPertainyms
    else:
        return None
    

# returns similarity based on the shortest hypernym path for every pair of synsets
def getSimilarity_wordnet(term1: str, term2: str, type1: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL, type2: WordTpyes_Wordnet=WordTpyes_Wordnet.ALL) -> list:
    similarites = []
    if type1 == WordTpyes_Wordnet.ALL:
        synsets1 = wn.synsets(term1)
    else:
        synsets1 = wn.synsets(term1, type1.value)

    if type2 == WordTpyes_Wordnet.ALL:
        synsets2 = wn.synsets(term2)
    else:
        synsets2 = wn.synsets(term2, type2.value)

    for syn1 in synsets1:
        for syn2 in synsets2:
            similarites.append(round(wn.path_similarity(syn1, syn2),2))
    # sort list descending
    similarites.sort(reverse=True)
    return similarites

# return a boolean of whether two terms are synonyms of each other
def areSynonyms_wordnet(term1: str, term2: str) -> bool:
    term1 = term1.lower()
    term2 = term2.lower()
    syns1 = getSynonyms_wordnet(term1)
    return term2 in syns1



def main():
    #print(getSimilarity_wordnet('length', 'duration', WordTpyes_Wordnet.NOUN, WordTpyes_Wordnet.NOUN))
    print(getHyperonyms_wordnet('written'))



if __name__ =="__main__":
    # nltk.download('wordnet')
    main()
