# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RussiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # part A
    licensee = scrapy.Field() # 持证商
    producer = scrapy.Field() # 生产商
    atx = scrapy.Field() # ATX
    active_ing = scrapy.Field() # 活性成分
    formulation = scrapy.Field() # 剂型
    name = scrapy.Field() # 药物名
    per_NO = scrapy.Field() # 注册号
    re_per = scrapy.Field() # 再注册日期
    exterior = scrapy.Field() # 外观
    sup = scrapy.Field() # 辅料
    # part B
    clinical = scrapy.Field() # 临床药理类
    med = scrapy.Field() # 药物治疗类
    influence = scrapy.Field() # 药理作用
    phar = scrapy.Field() # 药代动力学
    ind = scrapy.Field() # 适应症药物
    program = scrapy.Field() # 给药方案
    s_eff = scrapy.Field() # 副作用
    ban = scrapy.Field() # 禁忌
    special = scrapy.Field() # 特别说明
    excess = scrapy.Field() # 过量
    med_inter = scrapy.Field() # 药物相互作用
    pha_sale = scrapy.Field() # 药房销售条款
    storage = scrapy.Field() # 存储条款
    storage_time = scrapy.Field() # 保质期
    pass
