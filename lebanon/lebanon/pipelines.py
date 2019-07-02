# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class MongoPipeline(object):
    def __init__(self,mongo_uri,mongo_db,mongo_coll):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_coll = mongo_coll

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB'),
            mongo_coll=crawler.settings.get('MONGO_COLL')
        )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri,connect = False)
        self.db = self.client[self.mongo_db]

    def process_item(self,item,spider):

        # should use
        # name = item.__class__.name
        info_map = {"ATC": "ATC","bng":"B/G","ing":"Ingredients","code":"code","Nb":"Registration Nb","name":"Name",
                    "dosage":"Dosage","pres":"Presentation","form":"Form","route":"Route","agent":"Agent","lab":"Laboratory",
                    "country":"Country","price":"Price","phar":"Pharmacist Margin","stratum":"Stratum",
                    "party_name":"Responsible Party Name","party_country":"responsible Party Country",
                    "date":"Exch_date","down_title": "Drugs With Same Ingredients"}
        save_map = {}
        postItem = dict(item)
        for k, v in info_map.items():
            save_map[v] = postItem[k]
        self.db[self.mongo_coll].insert(save_map)
        return item

    def close_spider(self,spider):
        self.client.close()
