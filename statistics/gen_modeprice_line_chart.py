import pymongo 
import datetime 
import time
from scipy import stats as st
import numpy
from pprint import pprint


keyword = 'macbook h12'
db_url = 'mongodb://59.110.155.140:27017'
#db_url = 'mongodb://localhost:27017'
db_name = 'xianyu_exchange'

client = pymongo.MongoClient(db_url)
db = client[db_name]
coll = db[keyword]

idx = 0
for request in coll.find():
    idx = idx + 1
    items = request['items']
    all_price = []
    for item in items:
        price = int(item['price'])
        all_price.append(price)
    print "all_price:" + str(all_price)
    price_median = numpy.median(all_price)
    price_mode = st.mode(all_price)
    print str(idx) + ' mode is :'+str(price_mode) 
    print str(idx) + ' median is :'+str(price_median) 
