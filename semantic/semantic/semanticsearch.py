import os,sys
import csv,re,nltk
from nltk import bigrams
from stopwords import *
from itertools import chain
from Filter_stoplist import *
import nltk,json,MySQLdb
import cPickle as pickle
from datetime import *
from spellchecker import correct
from collections import defaultdict

def dbconnection():
    try:
        return MySQLdb.connect(host = 'localhost' , user = 'root',passwd = 'root', db ='skills')
    except Exception, e:
        return 'Error Unable to connect to MySQL Server'

def soft_skills():
    try:
        db = dbconnection()
        cur = db.cursor()
        dbq= "select skills from  SK_softskills_dictionary"
        cur.execute(dbq)
        rows = cur.fetchall()
        _sk = []
        for row in rows:
            _sk.append(row[0])
        return _sk
    except Exception,e:
        raise e
    finally:
        cur.close()
        db.commit()

def jobtitle():
    try:
        db = dbconnection()
        cur = db.cursor()
        dbq= "select distinct title from jobtitle where title IS NOT NULL or title != ''"
        cur.execute(dbq)
        rows = cur.fetchall()
        _title = []
        for row in rows:
            _title.append(row[0].strip().lower())
        return _title
    except Exception,e:
        raise e
    finally:
        cur.close()
        db.commit()

def skills_dict():
    try:
        db = dbconnection()
        cur = db.cursor()
        dbq= "select distinct skills from Identical_Skills where skills IS NOT NULL or skills != ''"
        cur.execute(dbq)
        rows = cur.fetchall()
        _sk = []
        for row in rows:
            _sk.append(row[0].strip().lower())
        return _sk
    except Exception,e:
        raise e
    finally:
        cur.close()
        db.commit()
def city_dict():
    try:
        db = dbconnection()
        cur = db.cursor()
        dbq= "select distinct state from tblcitylist where state IS NOT NULL or state != ''"
        cur.execute(dbq)
        rows = cur.fetchall()
        _state = []
        for row in rows:
            _state.append(row[0].strip().lower())
	cur1 = db.cursor()
	dbq1= "select distinct city_name from tblcitylist where city_name IS NOT NULL or city_name != ''"
        cur1.execute(dbq1)
        rows1 = cur1.fetchall()
        _city = []
        for row1 in rows1:
            _city.append(row1[0].strip().lower())
        
        return _city+_state

    except Exception,e:
        raise e
    finally:
	cur1.close()
        cur.close()
        db.commit()
def company_dict():
    try:
        db = dbconnection()
        cur = db.cursor()
        dbq= "select distinct company from company_list where company IS NOT NULL or company != ''"
        cur.execute(dbq)
        rows = cur.fetchall()
        _comp = []
        for row in rows:
            _comp.append(row[0].strip().lower())
        return _comp
    except Exception,e:
        raise e
    finally:
        cur.close()
        db.commit()

def remove_special_chars(text):
    return re.sub(r'[^a-zA-Z\/0-9-.,+ ]','', text).lower().replace(" "," ").replace(" to ","-").replace("- ","-").replace(" -","-")

def get_trigram(text,STOPWORDS):
    triwords = []
    trigram_filtered = nltk.trigrams([e.lower() for e in text.split(" ") if len(e) > 1])
    for i in trigram_filtered:
        triwords.append(str(i[0].lower())+" "+str(i[1].lower())+ " "+ str(i[2].lower()))
    return triwords

def get_bigram(text,STOPWORDS):
    biwords = []
    bigram_filtered = nltk.bigrams([e.lower() for e in text.split(" ") if len(e)>0 and e not in STOPWORDS])
    for i in bigram_filtered:
        biwords.append(str(i[0].lower())+" "+str(i[1].lower()))
    return biwords
def tree(): return defaultdict(tree)

def cfg_lexical_rule(tokens,job_title,identity_skills,company,location,logical_operators):
    #..Context free grammer rules for recognizing text grammer and lexical structure.
    #..Get part of speech for pos[i][0] created from text and create cfg.
    tag = {}
    pos = nltk.pos_tag(tokens)
    grammer_pattern = ",".join(i[1] for i in pos)
    year_rule = ['CD,NNS,CD,NNS','CD,-NONE-,CD','CD,CD','LS,NNS,CD,NNS']
    salary_rule = ['CD,NNS,JJ','JJR,IN,CD,NNS,JJ','CD,NN,NN','CD,JJ']
    experience_stack = {}
    logic_tag = tree()
    for elem in (pos):
        if len(elem[0]) < 4:
            if 'CD' in elem[1] or 'LS' in elem[1]:
                tag[elem[0]] = 'experience'
            else:
                pass
    print tokens
    negative_condition = ['not','nt','no','dont','donot','do not']
    positive_condition = ['or','and','only'] 
    for i in xrange(len(pos)):
	    
	if pos[i][0] not in logical_operators and  logic_tag.has_key(pos[i][0]) == False:
	    if pos[i][0] in identity_skills:
	        tag[pos[i][0]] = 'skill'
	    elif pos[i][0] in company:
		tag[pos[i][0]] = 'company'
	    elif pos[i][0] in  location:
		tag[pos[i][0]] = 'location'
	    elif pos[i][0] in job_title:
                tag[pos[i][0]] = 'job_title'
	    else:
		pass
	elif pos[i][0] in logical_operators and pos[i+1][0] not in logical_operators:
	    if pos[i+1][0] in location:
		logic_tag[pos[i+1][0]][pos[i][0]] = pos[i+1][0]
	    elif pos[i+1][0] in identity_skills:
		logic_tag[pos[i+1][0]][pos[i][0]] = pos[i+1][0]
	    elif pos[i+1][0] in company:
		logic_tag[pos[i+1][0]][pos[i][0]] = pos[i+1][0]
	    elif pos[i+1][0] in job_title:
		logic_tag[pos[i+1][0]][pos[i][0]] = pos[i+1][0]
	elif pos[i][0] in logical_operators and  pos[i+1][0] in location:
	    logic_tag[pos[i+1][0]][pos[i][0]] = pos[i+1][0]

	elif pos[i][0] in location and  pos[i-1][0] in location and pos[i-2][0] in logical_operators:
	    logic_tag[pos[i][0]][pos[i-2][0]] = pos[i][0]


	else:
	    pass
    tag['logical_tags'] = json.dumps(logic_tag.values())
    return tag


def main(query,job_title,identity_skills,company,location,logical_operators):
    stopwords = stopword()
    query = remove_special_chars(query.lower())
    tokens = [correct(q) for q in query.split() if q not in stopwords]
    tokens = tokens + get_bigram(query,stopwords) + get_trigram(query,stopwords)
    
    t1=  datetime.now()
    print cfg_lexical_rule(tokens,job_title,identity_skills,company,location,logical_operators)
    t2= datetime.now()
    print t2-t1
if __name__ == "__main__":
    logical_operators = ["or","not","dont","donot","don't","no","nt","only"]
    query = sys.argv[1]
    try:
	job_title = pickle.load(open("jobtitle.pkl","rb"))
        identity_skills = pickle.load(open("skills_corpora.pkl", "rb"))
    	company =  pickle.load(open("company_corpora.pkl","rb"))
	location =  pickle.load(open("location_corpora.pkl","rb"))
        flag = 0
    except Exception,e:
	raise e
	flag = 0
    if flag ==0:
	#try:
            #skills_corpus = skills_dict()
	    company_corpus = company_dict()
	    location_corpus = city_dict()
	    job_title = jobtitle()
 	    pickle.dump(job_title, open("jobtitle.pkl", "wb"))
            #pickle.dump(skills_corpus, open("skills_corpora.pkl", "wb"))
 	    pickle.dump(company_corpus, open("company_corpora.pkl", "wb"))
	    pickle.dump(location_corpus, open("location_corpora.pkl", "wb"))
            identity_skills = pickle.load(open("skills_corpora.pkl", "rb"))
	    job_title = pickle.load(open("jobtitle.pkl","rb"))
	    company =  pickle.load(open("company_corpora.pkl","rb"))
            location =  pickle.load(open("location_corpora.pkl","rb"))
    	    main(query,job_title,identity_skills,company,location,logical_operators)
	#except Exception,e:
	#    raise e
	    
    else:
	main(query,job_title,identity_skills,company,location,logical_operators)




