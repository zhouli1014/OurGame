# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DatacrawlsystemItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #date         = scrapy.Field()    
    #symbol       = scrapy.Field()
    #open         = scrapy.Field()
    #high         = scrapy.Field()
    #low          = scrapy.Field()
    #close        = scrapy.Field()
    #volume       = scrapy.Field()
    #amount       = scrapy.Field()
    #turnoverrate = scrapy.Field()

    date         = scrapy.Field()
    symbol       = scrapy.Field()
    open         = scrapy.Field()
    high         = scrapy.Field()
    low          = scrapy.Field()
    close        = scrapy.Field()
    change       = scrapy.Field()
    volume       = scrapy.Field()
    amount       = scrapy.Field()
    turnoverrate = scrapy.Field()
    change_5     = scrapy.Field()
    change_20    = scrapy.Field()
    change_60    = scrapy.Field()
    change_year  = scrapy.Field()
