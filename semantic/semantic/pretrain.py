import nltk
from nltk import bigrams
from stopwords import *
import cPickle as pickle
STOPWORDS = stopword()
def get_bigram(text,STOPWORDS):
    biwords = []
    bigram_filtered = nltk.bigrams([e.strip().lower() for e in text.split(" ") if len(e) >1 and e not in STOPWORDS])
    for i in bigram_filtered:
        biwords.append(str(i[0].lower())+" "+str(i[1].lower()))
    return biwords

def get_trigram(text,STOPWORDS):
    triwords = []
    trigram_filtered = nltk.trigrams([e.strip().lower() for e in text.split(" ") if len(e) >1])
    for i in trigram_filtered:
        triwords.append(str(i[0].lower())+" "+str(i[1].lower())+ " "+ str(i[2].lower()))
    return triwords

def train():
    sdict = []
    train = open('log.txt','r').read().split("\n")
    STOPWORDS = stopword()
    for i in train:
  	phrase =  get_bigram(i,STOPWORDS) + get_trigram(i,STOPWORDS)
        for j in phrase:
            sdict.append(j)
    pickle.dump(sdict, open("suggest.pkl", "wb"))
    print "ok"

if __name__=="__main__":
    train() 
