import re,nltk
from nltk import bigrams
from stopwords import *
import json
from datetime import *
import datetime
from knowledgebase import *
from suggester import correct
import logging
from datetime import datetime
import numbers
_format ='%(message)s'
logging.basicConfig(filename='/var/log/semantic_query.log',level=logging.INFO ,format=_format)


def autocheck(request):
    return json.dumps(correct(request))

def search(request):
    q = request
    try:
        _job_title = job_title().keys()
        identity_skills = skills().keys()
        _company = company().keys()
        _location = location().keys()
	logical_operators = ["or","not","no","nt","only","dont","don't"]
	return {"response":main(q,_job_title,identity_skills,_company,_location,logical_operators)}

    except Exception,e:
        return e
     
def remove_special_chars(text):
    return text.lower().replace(",","/").replace("- ","-").replace(" -","-").replace("\\","/").replace("&","and").replace(".","")

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
      
    
def tagger_rules(*args):
    tokens = args[0]
    job_title = args[1]
    identity_skills = args[2]
    company = args[3]
    location = args[4]
    logical_operators  = args[5]
    #..Get part of speech for tokens created from text and find data based on rules defined below.
    tag = {}
    part_of_speech = nltk.pos_tag(tokens)
    date_def = ['yrs','years','year','yr','exp','experience']
    month_def = ['months','month']
    currency_def = ['rs','rupees','rupee','inr','per','/','/yrs','/year','/years','/month','per month','/months']
    math_def =['<','>','&','!','>=','<=','<>','!=']
    spl_def = ['!','@','#','$','%','^','&','*','(',')','|']
    sal_def = ['more','greater','less','not less','higher','salary']
    for i in xrange(len(part_of_speech)):
        if len(part_of_speech[i][0]) < 4:
	    try:
	        if ('CD' in part_of_speech[i][1] or 'LS' in part_of_speech[i][1]) and ('-' in part_of_speech[i][0] or '/' in part_of_speech[i][0] and (part_of_speech[i+1][0] in date_def)):
			tag[part_of_speech[i][0]] = "years_experience"
		elif ('CD' in part_of_speech[i][1] or 'LS' in part_of_speech[i][1]) and (part_of_speech[i][0].isdigit() == True and int(part_of_speech[i][0]) <30 or isinstance(float(part_of_speech[i][0]), float) == True) and (part_of_speech[i+1][0] in date_def):
                	tag[part_of_speech[i][0]] = "years_experience"
	        elif ('CD' in part_of_speech[i][1] or 'LS' in part_of_speech[i][1]) and (part_of_speech[i][0].isdigit() == True and int(part_of_speech[i][0]) <30  or isinstance(float(part_of_speech[i][0]), float) == True) and  (part_of_speech[i+1][0] in month_def):
                	tag[part_of_speech[i][0]] = "month_experience"
        	elif ('CD' in part_of_speech[i][1] or 'LS' in part_of_speech[i][1]) and part_of_speech[i+1][0] in date_def or part_of_speech[i+1][0] in month_def:
	                tag[part_of_speech[i][0]] = "experience"        
        	elif ('CD' in part_of_speech[i][1] or 'LS' in part_of_speech[i][1]) and part_of_speech[i+1][0] in date_def:
                	tag[part_of_speech[i][0]] = "experience"
	        else:
        	    pass

	    except Exception,e:
		pass
    split_items = [',','/','-',':']
    for j in xrange(len(tokens)):
	key = tokens[j].encode(encoding='UTF-8',errors='strict')
	try:
	    item_index = (x for x in split_items if x in key).next()
	except:
	    item_index = ""
        if len(tokens) >1:
		if item_index != "" and ' ' not in key:
		    elem = key.split(item_index)
		    for e in elem:
			if 's' in e[-1:]:
			    e = e[:-1]
			else:
			    pass
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
		elif key in location and tokens[j-1] in logical_operators:
		    tag[tokens[j-1]+":"+key] = 'location'
		 
		elif key in identity_skills:
		    tag[key] = 'skill'
		elif key in company:
		    tag[key] = 'company'
		elif key in location and key not in identity_skills:
		    tag[key] = 'location'
		elif key in job_title:
		    tag[key] = 'job_title'
		else:
		    pass
	else:
	    if item_index != "" and ' ' not in key:
                    elem = key.split(item_index)
                    for e in elem:
                        if 's' in e[-1:]:
                            e = e[:-1]
                        else:
                            pass
                        if e in identity_skills:
                            tag[e] = 'skill'
                        if e in location:
                            tag[e] = 'location'
                        if e in company:
                            tag[e] = 'company'
                        if e in job_title:
                            tag[e] =  'job_title'
                        else:
                            pass
	    elif key in identity_skills:
                tag[key] = 'skill'
            elif key in company:
                tag[key] = 'company'
            elif key in location and key not in identity_skills:
                tag[key] = 'location'
            elif key in job_title:
                tag[key] = 'job_title'
            else:
                pass

    return tag


def main(*args):
    query = args[0]
    job_title = args[1]
    identity_skills = args[2]
    company = args[3]
    location = args[4]
    logical_operators = args[5]
    stopwords = stopword()
    query = remove_special_chars(query)
    log_string = str(query)
    logging.info(log_string)
    tokens = [q for q in query.split() if q not in stopwords]
    tokens = tokens + get_bigram(query,stopwords) + get_trigram(query,stopwords)
    return tagger_rules(tokens,job_title,identity_skills,company,location,logical_operators)
