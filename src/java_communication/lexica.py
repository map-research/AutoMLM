# this class bundles all the functions needed to communicate with the different lexicons and their apis

import nltk
from nltk.corpus import wordnet as wn
from enum import Enum

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

def getDistance_wordnet(lemma1 : str, lemma2 : str):

    l1 = wn.synset(lemma1)
    l2 = wn.synset(lemma2)

    return l1.shortest_path_distance(l2)





def main():
    #print(getLemmas_wordnet('length'))
    #print(getLemmas_wordnet('duration'))
    #print(getSimilarity_wordnet('oral', 'written'))
    #print(getSimilarity_wordnet('len'))
    #print(getPertainyms_wordnet('vocal'))
    #print(gethypernyms_wordnet('building'))
    #print(getSimilarity_wordnet('leads','works'))
    #print(getLemmas_wordnet('employee'))
    #print(getOwnerOfSynset_wordnet('course'))
    


    #print(getLowestCommonhypernym_wordnet('Cat','Dog'))


    #print(wn.synset("person.n.02").lemmas())   
    #print(getSynonyms_wordnet('Product'))

    #a = wn.synset("Building.n.02").hypernyms()
    #a = getDistance_wordnet('Dog.n.01','Cat.n.01')
    #path = l1._shortest_hypernym_paths(True)
    #print(path)


    #comm = getLowestCommonHypernym_wordnet('clerk.n.01','bartender.n.01')
    #print(comm)
    #print(getDepthLemma_wordnet(comm.name()))

    #c = getLemmas_wordnet('Cat', isLemmaOwner=False)
    #print(c)

    print(getLemmaOfRootHypernyms_wordnet('Cat'))


    print('Done')

    

if __name__ =="__main__":
    #check_wordnet()
    main()
