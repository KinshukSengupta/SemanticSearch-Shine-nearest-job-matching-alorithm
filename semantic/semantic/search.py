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
    return re.sub(r'[^a-zA-Z\/0-9-.,i&+ ]','', text).lower().replace(",","/").replace("- ","-").replace(" -","-").replace("\\","/").replace("&","and").replace("&&","and")

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
      
    
def cfg_lexical_rule(tokens,job_title,identity_skills,company,location,logical_operators):
    #..Get part of speech for tokens created from text and create cfg.
    tag = {}
    part_of_speech = nltk.pos_tag(tokens)
    grammer_pattern = ",".join(i[1] for i in part_of_speech)
    year_rule = ['CD,NNS,CD,NNS','CD,-NONE-,CD','CD,CD','LS,NNS,CD,NNS']
    salary_rule = ['CD,NNS,JJ','JJR,IN,CD,NNS,JJ','CD,NN,NN','CD,JJ']
    experience_stack = {}
    for i in (part_of_speech):
        if len(i[0]) < 4:
            if 'CD' in i[1] or 'LS' in i[1]:
                tag[i[0]] = 'experience'
            else:
                pass
    print tokens
    for j in xrange(len(tokens)):
	if '/' in tokens[j] and ' ' not in tokens[j]:
            elem = tokens[j].split("/")
            for e in elem:
		e= correct(e)
                if e in identity_skills:
                    tag[e] = 'skill'
                if e in location and tokens[j-1] in logical_operators:
                    tag[tokens[j-1]+":"+e] = 'location'
		if e in location and tokens[j-1] not in logical_operators:
                    tag[e] = 'location'
                if e in company:
                    tag[e] = 'company'
                if e in identity_skills and tokens[j+1] in job_title:
                    tag[e + " " + tokens[j+1]] = 'job_title'
                if e in job_title:
                    tag[e] =  'job_title'
                else:
                    pass

        elif tokens[j] in identity_skills and (tokens[j] not in company and tokens[j] not in location and tokens[j] not in job_title):
            tag[tokens[j]] = 'skill'
        elif tokens[j] in company and (tokens[j] not in identity_skills and tokens[j] not in location and tokens[j] not in job_title):
            tag[tokens[j]] = 'company'
        elif tokens[j] in location and tokens[j] not in identity_skills:
	    tag[tokens[j]] = 'location'
	elif tokens[j] in job_title:
	    tag[tokens[j]] = 'job_title'
	else:
	    pass
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
    logical_operators = ["or","not","no","nt","only","dont","don't"]
    query = sys.argv[1]
    try:
	job_title = pickle.load(open("jobtitle.pkl","rb"))
        identity_skills = pickle.load(open("skills_corpora.pkl", "rb"))
    	company =  pickle.load(open("company_corpora.pkl","rb"))
	location =  pickle.load(open("location_corpora.pkl","rb"))
        flag = 1
    except Exception,e:
	raise e
	flag = 0
    if flag ==0:
	#try:
	    print str(datetime.now())
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
	    print str(datetime.now())
	#except Exception,e:
	#    raise e
	    
    else:
	print str(datetime.now())
	main(query,job_title,identity_skills,company,location,logical_operators)
	print str(datetime.now())
