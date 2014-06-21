import cPickle as pickle
import anydbm
def job_title():
    return anydbm.open("memdb/jobtitle.mem","c") 
def skills():
    return anydbm.open("memdb/skills.mem", "c")
def company():
    return anydbm.open("memdb/company.mem", "c")
def suggestion_lst():
    #prefix_ = pickle.load(open("prefixTreeObject.pkl", "rb"))
    return anydbm.open("memdb/suggest.mem", "c")
def location():
    return anydbm.open("memdb/location.mem","c")

