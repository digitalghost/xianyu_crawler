import json
import codecs
import pymongo
from urllib import unquote
import urlparse 
import datetime
import time
import logging
import copy

class XianyuPipeline(object):
    def open_spider(self, spider):
        self.file =codecs.open('items_data_utf8.json','wh',encoding='utf-8')
    def close_spider(self, spider):
        self.file.close()
    def process_item(self,item,spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))
        return item

class MongoPipeline(object):
        def __init__(self, mongo_uri, mongo_db):
            self.mongo_uri = mongo_uri
            self.mongo_db = mongo_db
            logger = logging.getLogger(__name__)
            self.logger = logger

        @classmethod
        def from_crawler(cls, crawler):
            return cls(
                mongo_uri = crawler.settings.get('MONGO_URI'),
                mongo_db = crawler.settings.get('MONGO_DATABASE','items')
            )
        def open_spider(self, spider):
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
        def close_spider(self,spider):
            for val in spider.custom_settings['SEARCH_CRITERIA']:
                q = val['q'].decode('gbk')
                cache_key = 'cache_' + q
                self._save_batch_by_key(cache_key,spider,q)
            self.client.close()
        def process_item(self,item,spider):
            url = str(item['url'])
            qs = urlparse.urlsplit(url).query
            q = unquote(urlparse.parse_qs(qs)['q'][0]).decode('gbk')
            cache_key = "cache_" + q
            items_cache = spider.crawler.stats.get_value(cache_key)
            if items_cache == None:
                spider.crawler.stats.set_value(cache_key,[])
                items_cache = spider.crawler.stats.get_value(cache_key)
            items_cache.append(item)
            if len(items_cache) == spider.custom_settings['BATCH_MONGO_SAVE_CNT']:
                self._save_batch_by_key(cache_key,spider,q)
                
            return item
        def _save_batch_by_key(self,data_key,spider,q):
            data = spider.crawler.stats.get_value(data_key)

            if data == None or len(data) == 0:
                return
            data = copy.deepcopy(data)
            spider.crawler.stats.set_value(data_key,[])
            query = {"keyword":q,"request_id":spider.crawler.stats.get_value("request_id")}
            result = self.db[q].find_one(query)
            if result != None:
                self.db[q].update(query, {'$push': {'items': {'$each':data}}})
            else:
                new_doc = {
                        "keyword":q,
                        "request_id":spider.crawler.stats.get_value("request_id"),
                        "last_modified": datetime.datetime.utcnow(),
                        "items":data
                       }
                self.db[q].insert_one(new_doc)
        def process_item2(self,item,spider):
            url = str(item['url'])
            qs = urlparse.urlsplit(url).query
            q = unquote(urlparse.parse_qs(qs)['q'][0]).decode('gbk')
            new_doc = {
                        "keyword":q,
                        "request_id":spider.crawler.stats.get_value("request_id"),
                        "last_modified": datetime.datetime.utcnow(),
                        "items":[item]
                       }

            #query = {'xianyu_id':item['xianyu_id']} 
            #self.db[q].update(query, item,upsert=True)
            query = {"keyword":q,"request_id":spider.crawler.stats.get_value("request_id")}
            if result != None:
                self.db[q].update(query, {'$push': {'items': item}})
            else:
                self.db[q].insert_one(new_doc)
            return item



class ExchangeTotalSavePipeline(object):
    mongo_uri = None 
    mongo_db = None
    client = None
    db = None
    logger = None
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DATABASE','items')
        )

    def open_spider(self, spider):
        logger = logging.getLogger(__name__)
        self.logger = logger
        pass
    def close_spider(self, spider):
        #Iterate for search criteria to calculate the exchange info
        for cri in spider.settings.get('SEARCH_CRITERIA'):
            keyword = cri['q'].decode('gbk')
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            coll = self.db[keyword]
            coll_exchange = self.db[keyword + '_exchange']
            #for request in coll.find():
            #    requests.append(request)
            #for req_idx,request in enumerate(requests):
            req_idx = 0
            request_prev = None
            for request in coll.find():
                if req_idx == 0 :
                    req_idx = req_idx + 1
                    request_prev = request
                    continue
                increase_items = []
                decrease_items = []
                items1 = request_prev['items']
                items2 = request['items']
                for item1 in items1:
                    founded = False
                    for item2 in items2:
                        if item1['xianyu_id'] == item2['xianyu_id']: 
                            founded = True
                    if founded == True:
                        continue
                    else:
                        decrease_items.append(item1)
                for item2 in items2:
                    founded = False
                    for item1 in items1:
                        if item2['xianyu_id'] == item1['xianyu_id']: 
                            founded = True
                    if founded == True:
                        continue
                    else:
                        increase_items.append(item2)
                self.logger.info("Request " + str(req_idx-1) + " and Request " + str(req_idx))
                self.logger.info("+ " + str(len(increase_items)) + " items")
                if len(increase_items) != 0:
                    for item in increase_items:
                        self.logger.info("**+item: " + item['title'])
                self.logger.info("- " + str(len(decrease_items)) + " items")
                if len(decrease_items) != 0:
                    for item in decrease_items:
                        self.logger.info("**-item: " + item['title'])
                self.logger.info("==================================")

                exchange_id = keyword + '_' + str(request_prev['last_modified']) + str(request['last_modified'])
                coll_exchange.update( { "exchange_id": exchange_id},
                            {'exchange_id':exchange_id,
                                'inc':increase_items,
                                'dec':decrease_items,
                                'compare_start':request_prev['last_modified'],
                                'compare_end':request['last_modified']},
                            True)
                req_idx = req_idx + 1
                request_prev = request

        self.client.close()
        self.logger.info("Exchange Save close," + keyword)

class ExchangeSavePipeline(object):
    mongo_uri = None 
    mongo_db = None
    client = None
    db = None
    logger = None
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DATABASE','items')
        )

    def open_spider(self, spider):
        logger = logging.getLogger(__name__)
        self.logger = logger
        pass
    def close_spider(self, spider):
        #Iterate for search criteria to calculate the exchange info
        for cri in spider.settings.get('SEARCH_CRITERIA'):
            keyword = cri['q'].decode('gbk')
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            coll = self.db[keyword]
            coll_exchange = self.db[keyword + '_exchange']
            #for request in coll.find():
            #    requests.append(request)
            #for req_idx,request in enumerate(requests):
            req_idx = 0
            request_next = None
            itr = coll.find({},sort=[("last_modified", pymongo.DESCENDING)],limit=2)
            for request in itr :
                if req_idx == 0 :
                    req_idx = req_idx + 1
                    request_next = request
                    continue
                increase_items = []
                decrease_items = []
                items1 = request['items']
                items2 = request_next['items']
                for item1 in items1:
                    founded = False
                    for item2 in items2:
                        if item1['xianyu_id'] == item2['xianyu_id']: 
                            founded = True
                    if founded == True:
                        continue
                    else:
                        decrease_items.append(item1)
                for item2 in items2:
                    founded = False
                    for item1 in items1:
                        if item2['xianyu_id'] == item1['xianyu_id']: 
                            founded = True
                    if founded == True:
                        continue
                    else:
                        increase_items.append(item2)
                self.logger.info("Request " + str(req_idx-1) + " and Request " + str(req_idx))
                self.logger.info("+ " + str(len(increase_items)) + " items")
                if len(increase_items) != 0:
                    for item in increase_items:
                        self.logger.info("**+item: " + item['title'])
                self.logger.info("- " + str(len(decrease_items)) + " items")
                if len(decrease_items) != 0:
                    for item in decrease_items:
                        self.logger.info("**-item: " + item['title'])
                self.logger.info("==================================")

                exchange_id = keyword + '_' + str(request['last_modified']) + str(request_next['last_modified'])
                coll_exchange.update( { "exchange_id": exchange_id},
                            {'exchange_id':exchange_id,
                                'inc':increase_items,
                                'dec':decrease_items,
                                'compare_start':request['last_modified'],
                                'compare_end':request_next['last_modified']},
                            True)

        self.client.close()
        self.logger.info("Exchange Save close")
