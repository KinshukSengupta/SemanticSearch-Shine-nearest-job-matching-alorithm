## Spell checking and corrector algorithm based on bayes probability to find best word for misspelled words.
## Accuracy ~ 90%
## Trained on indentical skills corpus.
## ........................................................................................................
import re,collections
from nltk import bigrams
from stopwords import *
import cPickle as pickle
from knowledgebase import suggestion_lst
STOPWORDS = stopword()
def get_bigram(text,STOPWORDS):
    biwords = []
    bigram_filtered = nltk.bigrams([correct(e.strip().lower()) for e in text.split(" ") if len(e) >1 and e not in STOPWORDS])
    for i in bigram_filtered:
        biwords.append(str(i[0].lower())+" "+str(i[1].lower()))
    return biwords

def get_trigram(text,STOPWORDS):
    triwords = []
    trigram_filtered = nltk.trigrams([correct(e.strip().lower()) for e in text.split(" ") if len(e) >1])
    for i in trigram_filtered:
        triwords.append(str(i[0].lower())+" "+str(i[1].lower())+ " "+ str(i[2].lower()))
    return triwords


def words(text): 
    return re.findall('[a-z0-9]+', text.lower())

def train(features):
    model = collections.defaultdict(lambda: 2)
    for f in features: 
        model[f] += 2
    return model

NWORDS = train(words(file('spellings.pkl').read()))

alphabet = 'abcdefghijklmnopqrstuvwxyz'
  

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(words):
    item = words.split()
    word = item[len(item) -1]
    item.pop(len(item) -1)
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    tag = " ".join(x for x in item)
    #..P(phrase|word_typed) = P(word_typed|phrase) P(phrase) / P(word_typed)
    suggestion = suggestion_lst()
    store = filter(lambda x: tag in x, suggestion)
    resp = [tag +" " + max(candidates, key=NWORDS.get)] + store[:4]
     
    return {"term":resp}

    
