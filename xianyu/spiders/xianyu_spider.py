# -*- coding: utf-8 -*-
from urllib import urlencode
import scrapy
from xianyu.items import XianyuItem
import urlparse
import datetime

class XianyuSpider(scrapy.Spider):
    name = "xianyu"
    #start_urls = [
    #    'https://s.2.taobao.com/list/list.htm?spm=2007.1000337.6.3.Jx7Ika&divisionId=110100&st_price=1&q=iphone+se+64&ist=0',
    #]
    custom_settings = {
        'SEARCH_CRITERIA':[
            {'q':u'iphone se 64','ist':'0','st_edtime':'1'},
            {'q':u'nintendo switch','ist':'0','st_edtime':'1'},
            #{'q':u'求购'.encode('gbk'),'ist':'0','st_edtime':'1','divisionId':'110100'},
            {'q':u'小米 mix 256gb'.encode('gbk'),'ist':'0','st_edtime':'1'},
            {'q':u'Casio tr600'.encode('gbk'),'ist':'0','st_edtime':'1',},
            {'q':'iphone 7 128gb','ist':'0','st_edtime':'1'},
            {'q':'iphone 7 256gb','ist':'0','st_edtime':'1'},
            {'q':'iphone 7 plus 128gb','ist':'0','st_edtime':'1'},
            {'q':'iphone 7 plus 256gb','ist':'0','st_edtime':'1'},
            {'q':'iphone 7 64gb','ist':'0','st_edtime':'1'},
        ],
        'ITEM_PIPELINES': {
            'xianyu.pipelines.MongoPipeline': 100,
            'xianyu.pipelines.ExchangeSavePipeline': 99,
        },
        'BATCH_MONGO_SAVE_CNT':200

    }

    def start_requests(self):
        stats = self.crawler.stats
        stats.set_value("request_id","rid_"+str(datetime.datetime.utcnow()))
        base_url = 'https://s.2.taobao.com/list/list.htm?'
        for val in self.custom_settings['SEARCH_CRITERIA']:
            request_url = base_url + urlencode(val)
            yield scrapy.Request(request_url)

    def parse(self, response):
        for quote in response.css('li.item-info-wrapper'):
            #print quote.css('h4.item-title > a::text').extract_first().encode("utf-8")
            detail_url = quote.css('h4.item-title > a::attr(href)').extract_first()
            item = XianyuItem()
            item['url'] = response.url
            qs = urlparse.urlsplit(detail_url).query
            item['xianyu_id'] = urlparse.parse_qs(qs)['id'][0]
            item['title'] = quote.css('h4.item-title > a::text').extract_first().encode("utf-8")
            item['price'] = float(str(quote.css('span.price > em::text').extract_first()))
            item['desc'] = quote.css('div.item-description::text').extract_first().encode("utf-8")
            item['last_update'] = quote.css('span.item-pub-time::text').extract_first().encode("utf-8")
            item['detail_url'] = 'https:' +  quote.css('h4.item-title > a::attr(href)').extract_first()
            item['seller_loc'] = quote.css('div.seller-location::text').extract_first().encode("utf-8")
            item['seller_uid'] = quote.css('div.seller-nick > span::attr(data-nick)').extract_first()
            yield item
        next_page = response.css('div#J_Pages.paginator > a.paginator-next::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page,callback=self.parse)
    
    def __extract_uid(self,url):
        qs = urlparse.urlsplit(url).query
        return str(urlparse.parse_qs(qs)['uid'][0])




# Need login, Blocked
#    def parse_item_detail(self, response):
#        item = XianyuItem()
#        item['url'] = response.url
#        qs = urlparse.urlsplit(item['url']).query
#        item['xianyu_id'] = urlparse.parse_qs(qs)['id'][0]
#        item['title'] = quote.css('div#J_Property.property > h1.title::text').extract_first().encode("utf-8")
#        item['price'] = float(str(quote.css('span.price.big > em::text').extract_first()))
#        timestring = quote.css('#idle-detail > div.top-nav.clearfix > div.others-wrap > ul > li:nth-child(2) > span::text').extract_first()
#        item['last_update'] = datetime.strptime(timestring, '%Y-%m-%d %H:%M')
#        yield item
#
