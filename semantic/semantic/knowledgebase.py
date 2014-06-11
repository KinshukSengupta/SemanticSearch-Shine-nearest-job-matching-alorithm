import cPickle as pickle
def job_title():
    return pickle.load(open("jobtitle.pkl","rb"))

def skills():
    return pickle.load(open("skills_corpora.pkl", "rb"))

def company():
    return pickle.load(open("company_corpora.pkl","rb"))
def suggestion_lst():
    return pickle.load(open("suggest.pkl","rb"))      
def location():
    return pickle.load(open("location_corpora.pkl","rb"))

