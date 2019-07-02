# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LebanonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # upper_title = scrapy.Field()
    down_title = scrapy.Field()
    ATC = scrapy.Field()
    bng = scrapy.Field()
    ing = scrapy.Field()
    code = scrapy.Field()
    Nb = scrapy.Field()
    name = scrapy.Field()
    dosage = scrapy.Field()
    pres = scrapy.Field()
    form  = scrapy.Field()
    route = scrapy.Field()
    agent = scrapy.Field()
    lab = scrapy.Field()
    country = scrapy.Field()
    price = scrapy.Field()
    phar = scrapy.Field()
    stratum = scrapy.Field()
    party_name = scrapy.Field()
    party_country = scrapy.Field()
    date = scrapy.Field()
    pass
