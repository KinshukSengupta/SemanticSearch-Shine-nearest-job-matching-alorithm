import nltk,os,sys
from nltk import bigrams
import cPickle as pickle
import MySQLdb
import anydbm,re
from pytrie import SortedStringTrie as trie
from regularwords import *
import collections
def get_bigram(text,STOPWORDS):
    biwords = []
    text = words(text)
    bigram_filtered = nltk.bigrams([e.strip().lower() for e in text.split(" ") if len(e) >1 and e not in STOPWORDS])
    for i in bigram_filtered:
        biwords.append(str(i[0].lower())+" "+str(i[1].lower()))
    return biwords

def get_trigram(text,STOPWORDS):
    triwords = []
    text = words(text)
    trigram_filtered = nltk.trigrams([e.strip().lower() for e in text.split(" ") if len(e) >1 and e not in STOPWORDS])
    for i in trigram_filtered:
        triwords.append(str(i[0].lower())+" "+str(i[1].lower())+ " "+ str(i[2].lower()))
    return triwords

def dbconnection():
    try:
        return MySQLdb.connect(host = '172.22.67.37' , user = 'sumoplus',passwd = 'sumoplus', db ='SumoPlus')
    except Exception, e:
        return 'Error Unable to connect to MySQL Server'

def job_attribute_skills():
    try:
        db = dbconnection()
	db1 = anydbm.open('memdb/job_attribute.mem','c')
	db2 = anydbm.open('memdb/id_to_skills.mem','c')
	db3 = anydbm.open('memdb/id_to_city.mem','c')
	city_lookup = anydbm.open('memdb/city_lookup.mem','c')
        if not db1 or not db2 or not db3:
		db1 = anydbm.open('memdb/job_attribute.mem','c')
	        db2 = anydbm.open('memdb/id_to_skills.mem','c')
        	db3 = anydbm.open('memdb/id_to_city.mem','c')
		cur = db.cursor()
	        q1= "SELECT jobid,CONCAT(`jobtitle`, '->', `salarymin`,' to ' , salarymax , '->' , minexperience ,' to ',maxexperience ,'->' , searchquery) FROM recruiter_job"
        	cur.execute(q1)
	        rows = cur.fetchall()
        	for row in rows:
		    if row[0] != "" or row[0] != None:
			try:
	        	    db1[str(row[0])] = str(row[1])
			except:
			    pass
		    else:
			pass
		print "Completed 1st Database Fetch"
		cur1 = db.cursor()
	 	q2 = "SELECT  jobid_id,AttValueCustom from recruiter_jobattribute where  groupid =400"
		cur1.execute(q2)
	  	data = cur1.fetchall()
		for row1 in data:
		    db2[str(row1[0])] = row1[1]
			
		print "Completed 2nd Database Fetch"
		q3 = "SELECT jobid_id,AttValue FROM recruiter_jobattribute where AttType=13"
		cur2 = db.cursor()
		cur2.execute(q3)
		data2 = cur2.fetchall()
		for row2 in data2:
		    db3[str(row2[0])] = str(row2[1])
		print "Completed 3rd Database Fetch"
		print "Starting building dictionary"
		for all_keys in db1.keys():
		    try:
		        db1[str(all_keys)] = db1[str(all_keys)].split("->")[0] + " in " + city_lookup[db3[str(all_keys)]] + ":" + db2[str(all_keys)]
		    except Exception,e:
			print e
		cur.close()
		cur1.close()
		cur2.close()
		
	else:
	    print "Starting building dictionary"
            for all_keys in db1.keys():
     		try: 
                    db1[str(all_keys)] = db1[str(all_keys)].split("->")[0] + " in " + city_lookup[db3[str(all_keys)]] + ":" + db2[str(all_keys)]
		except Exception,e:
		    print e
	db1.close()
	db2.close()
	db3.close()
 	return 'OK'	
    except Exception,e:
        raise e
    finally:
        db.commit()
def find_word(text, search):

   result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
   if len(result)>1:
      return True
   else:
      return False

def remove_stopwords(text):
    STOPWORDS = stopword()
    text =  text.lower()
    for words in STOPWORDS:
	check = re.findall('\\b'+words+'\\b', text, flags=re.IGNORECASE)
	if len(check) >=1:
            text = text.replace(i,"").replace(" ,",",").replace(", ",",").replace(" / ","/").replace("/ ","/").replace(" /","/").replace(",  ",",").replace("  ","").replace("   ","")
	else:
	    text = text.replace(" ,",",").replace(", ",",").replace(" / ","/").replace("/ ","/").replace(" /","/").replace(",  ",",").replace("  ","").replace("   ","")
    text = re.sub(r'\([^)]*\)', '',text)
    text = re.sub(r'[^a-zA-Z\/,.-24 ]','', text)
    return text
    
def train(flag):
    import logging
    import anydbm
    _format ='%(message)s'
    logging.basicConfig(filename='/var/log/pretrain.log',level=logging.INFO ,format=_format)
    STOPWORDS = stopword()
    #db = collections.defaultdict(list)
    if flag =="1":
        job_attribute_skills()
	inmemory_dataset = anydbm.open('memdb/job_attribute.mem', 'c')
        db = anydbm.open('memdb/suggest.mem', 'c')
	for v in inmemory_dataset.values():
            phrase = v.split(":")
            if v == 'None':
                pass
	    else:
	        for i in xrange(len(phrase)):
                    if len(phrase[i]) <=2:
                        pass

                    elif 'None' in phrase[i]:
                        pass
                    else:
                        try:
                            phrase[i] =  remove_stopwords(phrase[i].decode('utf-8').strip())
                            phrase[i+1] =  remove_stopwords(phrase[i+1].decode('utf-8').strip())
                            token = phrase[i] + "with skills" +phrase[i+1]
                            tokens = [phrase[i]] + [token] + get_trigram(token,STOPWORDS)
                            for j in tokens:
				
                                db[str(j.decode('utf-8').strip())] = str(j.decode('utf-8').strip())
                        except:
                            pass
        #pickle.dump(pd.items(), open("prefixTreeObject.pkl", "wb"))
        db.close()
	inmemory_dataset.close()
        logging.info('Training of Offline Model completed-1!')
        print "Training of Offline Model completed -1!"
    else:
	inmemory_dataset = anydbm.open('memdb/job_attribute.mem', 'c')
	db = anydbm.open('memdb/suggest.mem', 'c')
	for v in inmemory_dataset.values():
	    phrase = v.split(":")
	    if v == 'None':
	        pass
	    else:
	        for i in xrange(len(phrase)):
		    if len(phrase) <=2:
			pass
		    
		    elif 'None' in phrase[i]:
			pass
		    
		    else:
			try:
			    logging.info(phrase)
			    phrase[i] =  remove_stopwords(phrase[i])
			    db[str(phrase[i].decode('utf-8').strip())] = str(phrase[i].decode('utf-8').strip())
                            #token = phrase[i] + "with skills" +phrase[i+1]
			    ''' 
			    for j in phrase[i+1].split(","):
                                db[str(j.decode('utf-8').strip())] = str(j.decode('utf-8').strip())
			    '''
                        except:
                            pass
	#pickle.dump(db, open("prefixTreeObject.pkl", "wb"))
	db.close()
	inmemory_dataset.close()
	logging.info('Training of Offline Model completed-2!')
	print "Training of Offline Model completed -2!"

if __name__=="__main__":
    remove_stopwords(sys.argv[1])
