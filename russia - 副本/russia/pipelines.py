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
        info_map = {"licensee": "Владелец регистрационного удостоверения", "producer": "Произведено", "atx": "Код ATX",
                    "active_ing": "Активное вещество", "formulation": "Лекарственная форма",
                    "name": "Торговое наименованиелекарственного препарата", "per_NO": "рег №",
                    "re_per": "Дата перерегистрации", "exterior": "Форма выпуска, упаковка и состав",
                    "sup": "Вспомогательные вещества", "clinical": "Клинико-фармакологич группа",
                    "med": "Фармако-терапевтическая группа", "influence": "Фармакологическое действие",
                    "phar": "Фармакокинетика", "ind": "Показания препарата",
                    "program": "Режим дозирования", "s_eff": "Побочное действие",
                    "ban": "Противопоказания к применению", "special": "Особые указания", "excess": "Передозировка",
                    "med_inter": "Лекарственное взаимодействие", "pha_sale": "Условия отпуска из аптек",
                    "storage": "Условия хранения", "storage_time": "Срок годности"}
        save_map = {}
        postItem = dict(item)
        for k, v in info_map.items():
            save_map[v] = postItem[k]
        self.db[self.mongo_coll].insert(dict(item))
        return item

    def close_spider(self,spider):
        self.client.close()


