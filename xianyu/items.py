# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item,Field

class XianyuItem(scrapy.Item):
    # define the fields for your item here like:
    xianyu_id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    desc = scrapy.Field()
    last_update = scrapy.Field()
    detail_url = scrapy.Field()
    seller_loc = scrapy.Field()
    seller_uid = scrapy.Field()
