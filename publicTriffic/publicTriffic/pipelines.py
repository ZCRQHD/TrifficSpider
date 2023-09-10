# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import shelve
from json import dump
class PublictrifficPipeline:
    def open_spider(self,spider):
        self.dict = {
            'busData' : {}
        }


    def process_item(self, item, spider):
        province = item['province']
        city = item['city']
        self.dict['busData'][province] = self.dict['busData'].get(province,{})
        self.dict['busData'][province][city] = self.dict['busData'][province].get(city,{})
        self.dict['busData'][province][city][item['busType']] = self.dict['busData'][province][city]\
            .get(item['busType'],[])
        self.dict['busData'][province][city][item['busType']].append(dict(item))
        print("successfully append {} {} {} {}".format(province,city,item['busType'],item['name']))
        return item
#
# class WebSpider:
#     def process_item(self, item, spider):
#         print(item)
    def close_spider(self, spider):
        jsonFile = open("busData.json","w")
        dump(self.dict,jsonFile,ensure_ascii=False)
        jsonFile.close()