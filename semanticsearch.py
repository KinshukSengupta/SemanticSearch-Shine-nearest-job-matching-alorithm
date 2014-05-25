import os,sys
import csv,re,nltk
from nltk import bigrams
from stopwords import *
from itertools import chain
from Filter_stoplist import *
import nltk,json,MySQLdb
import cPickle as pickle

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

def follow_grammer(grammer):
    grammer_rules = []
def cfg_lexical_rule(tokens,identity_skills,company,location,logical_operators):
    #..Context free grammer rules for recognizing text grammer and lexical structure.
    #..Get part of speech for tokens created from text and create cfg.
    tag = {}
    part_of_speech = nltk.pos_tag(tokens)
    for i in part_of_speech:
	if 'CD' in i[1]:
	    tag[i[0]] = 'experience'
            
    for token in tokens:
	if token in identity_skills and token not in company and token not in location:
		tag[token] = 'skill'
	elif token in company and token not in identity_skills and token not in location:
		tag[token] = 'company'
	elif token in location and token not in company and token not in identity_skills:
		tag[token] = 'location'	
	else:
		pass	
    return tag
	
def main(query,identity_skills,company,location,logical_operators):
    stopwords = stopword() 
    tokens = [q for q in query.split() if q not in stopwords]
    return cfg_lexical_rule(tokens,identity_skills,company,location,logical_operators)
if __name__ == "__main__":
    logical_operators = ['or','and','only','not']
    query = sys.argv[1]
    try:
        identity_skills = pickle.load(open("skills_corpora.pkl", "rb"))
    	company =  pickle.load(open("company_corpora.pkl","rb"))
	location =  pickle.load(open("location_corpora.pkl","rb"))
        flag = 1
    except Exception,e:
	flag = 0
    if flag ==0:
	try:
	    
            skills_corpus = skills_dict()
	    company_corpus = company_dict()
	    location_corpus = city_dict()
            pickle.dump(skills_corpus, open("skills_corpora.pkl", "wb"))
 	    pickle.dump(company_corpus, open("company_corpora.pkl", "wb"))
	    pickle.dump(location_corpus, open("location_corpora.pkl", "wb"))
            identity_skills = pickle.load(open("skills_corpora.pkl", "rb"))
	    company =  pickle.load(open("company_corpora.pkl","rb"))
            location =  pickle.load(open("location_corpora.pkl","rb"))
    	    print main(query,identity_skills,company,location,logical_operators)
	except Exception,e:
	    raise e
	    
    else:
	print main(query,identity_skills,company,location,logical_operators)
