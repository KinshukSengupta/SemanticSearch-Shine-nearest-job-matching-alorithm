## Spell checking and corrector algorithm based on bayes probability to find best word for misspelled words.
## Accuracy ~ 90%
## Trained on indentical skills corpus.
## ngram implementation for intent skills/suggestion
## ........................................................................................................
import re,collections
from nltk import bigrams
from stopwords import *
from knowledgebase import suggestion_lst
import re, math
from collections import Counter
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

NWORDS = train(words(file('memdb/spellings.pkl').read()))
alphabet = 'abcdefghijklmnopqrstuvwxyz'
WORD = re.compile(r'\w+')

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

def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])
     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)
     if not denominator:
        return 0.0
     else:
        return (float(numerator) / denominator)*100
def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)

def correct(words):
    from prefixtree import PrefixDict
    words = words.strip().lower()
    item = words.split()
    suggestion = suggestion_lst()
    if len(item) != 1:
        word = item[len(item) -1]
        item.pop(len(item) -1)
	candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
        tag = " ".join(x.strip() for x in item)
        store =  sorted([x for x in suggestion.keys() if tag.strip() in x and get_cosine(text_to_vector(tag.strip()), text_to_vector(x.strip())) > 40])
	#store = sorted([x for x in set(suggestion.get(tag[:1])) if tag in x and get_cosine(text_to_vector(tag.strip()), text_to_vector(x.strip())) > 50])

        resp = list(set([(tag +" " + max(candidates, key=NWORDS.get)).strip()] + store[:5]))
        return {"term":resp[::-1]}

    else:
        word = item[0]
        candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
        tag = " ".join(x.strip() for x in item)
        store =  sorted([x for x in suggestion.keys() if tag.strip() in x and get_cosine(text_to_vector(tag.strip()), text_to_vector(x.strip())) > 40])
	#store = sorted([x for x in set(suggestion.get(tag[:1])) if tag in x and get_cosine(text_to_vector(tag.strip()), text_to_vector(x.strip())) > 50])
        resp = list(set([(max(candidates, key=NWORDS.get)).strip()] + store[:5]))
        return {"term":resp[::-1]}
