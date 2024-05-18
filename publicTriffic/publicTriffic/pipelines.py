# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import shelve
from json import dump
import peewee

import pymysql
from pympler.asizeof import asizeof

setting = shelve.open('publicTriffic/db/SQL')
settingDict = setting['db']
db = peewee.MySQLDatabase(
    host=settingDict['host'],
    port=settingDict['port'],
    user=settingDict["user"],
    password=settingDict['password'],
    database=settingDict['DBname']

)


class Line(peewee.Model):
    id = peewee.CharField()
    name = peewee.TextField()
    pairCode = peewee.CharField()
    preOpen = peewee.IntegerField()
    province = peewee.TextField()
    city = peewee.TextField()
    company = peewee.TextField()

    class Meta:
        database = db
        db_table = "line"


# Line.create(id="123",
#             name="34",
#             preOpen=2,
#             pairCode="zxc",
#             province="svg",
#             city='1',
#             company='23',
#             er=234
#
#             )


class SaveDBPipeline:

    def open_spider(self, spider):
        spider.log("DB pipline has started")

    def process_item(self, item, spider):
        pass

    def close_spider(self, spider):
        pass


class SaveJsonPipeline:
    def open_spider(self, spider):
        spider.log("save")
        self.dict = {
            'busData': {}
        }

    def process_item(self, item, spider: scrapy.Spider):
        province = item['province']
        city = item['city']
        spider.log(f"the size of {item['province']} {item['city']} {item['name']} is {asizeof(item)}")
        self.dict['busData'][province] = self.dict['busData'].get(province, {})
        self.dict['busData'][province][city] = self.dict['busData'][province].get(city, {})
        self.dict['busData'][province][city][item['busType']] = self.dict['busData'][province][city] \
            .get(item['busType'], [])
        self.dict['busData'][province][city][item['busType']].append(dict(item))
        spider.log("successfully append {} {} {} {}".format(province, city, item['busType'], item['name']))
        return item

    #
    # class WebSpider:
    #     def process_item(self, item, spider):
    #         print(item)
    def close_spider(self, spider):
        fileName = "publicTriffic/result/baidu.json" if spider.name == "baidu" else "publicTriffic/result/8684.json"
        jsonFile = open(fileName, "w")
        dump(self.dict, jsonFile, ensure_ascii=False)
        jsonFile.close()
