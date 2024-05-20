# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import math
# useful for handling different item types with a single interface
import shelve
from json import dump

import bd09convertor
import scrapy
from pympler.asizeof import asizeof
from .ORM import *

x_pi = math.pi * 3000.0 / 180.0

a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


class SaveDBPipeline:
    def convert(self, lan, lot):
        bd_lon, bd_lat = bd09convertor.convertMC2LL(lan, lot)
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return [gg_lng, gg_lat]
    def open_spider(self, spider):
        spider.log("DB pipline has started")

    def process_item(self, item, spider: scrapy.Spider):
        if spider.name == 'baidu':
            Line.create(
                id=item['uid'],
                name=item['name'],
                pairCode=item['pairCode'],
                preOpen=item['preOpen'],
                province=item['province'],
                city=item['city'],
                company=item['company']
            )
            spider.log("succcessfully save line {} id={} to datatbase".format(item['name'], item['code']))
            for platform in item['stationList']:
                hashResult = hashlib.sha256(platform[1])
                platform_uid = hashResult.hexdigest()
                result = Platform.select().where(Platform.id == platform_uid)
                if len(result) == 0:
                    lan, lot = platform[1].split(',')
                    geox, geoy = self.convert(float(lan), float(lot))
                    Platform.create(
                        id=platform_uid,
                        geox=geox,
                        geoy=geoy,
                        station=platform[0]

                    )
                    spider.log("succcessfully save platform {} id={} to datatbase".format(
                        platform[2], platform_uid))
                    del lan, lot, geox, geoy
                LineStation.create(
                    line=item['code'],
                    platform=platform_uid
                )
                result = Station.select().where(Station.id == platform[0])
                hashResult = hashlib.sha256(
                    ",".join([item['province'], item['city'], item["name"]])
                )
                mainStation_uid = hashResult.hexdigest()
                if len(result) == 0:
                    Station.create(
                        id=platform[0],
                        mainStation=mainStation_uid
                    )
                result = MainStation.select().where(MainStation.id == mainStation_uid)
                if len(result) == 0:
                    MainStation.create(
                        province=item['province'],
                        city=item['city'],
                        name=item['name'],
                        id=mainStation_uid

                    )
            pathList = [
                tuple([item['code']] + self.convert(float(lan), lot)) for lan, lot in item['path']
            ]
            Path.insert_many(pathList, fields=[Path.line, Path.geox, Path.geoy])
        return item






    def close_spider(self, spider):
        db.close()
        spider.log("successfully closed database")


class SaveJsonPipeline:
    def open_spider(self, spider):
        self.db = shelve.open('publicTriffic/db/jsonCache','c')

    def process_item(self, item, spider: scrapy.Spider):
        province = item['province']
        city = item['city']
        spider.log(f"the size of {item['province']} {item['city']} {item['name']} is {asizeof(item)}")
        self.db['busData'][province] = self.db['busData'].get(province, {})
        self.db['busData'][province][city] = self.db['busData'][province].get(city, {})
        self.db['busData'][province][city][item['busType']] = self.db['busData'][province][city] \
            .get(item['busType'], [])
        self.db['busData'][province][city][item['busType']].append(dict(item))
        spider.log("successfully append {} {} {} {}".format(province, city, item['busType'], item['name']))
        return item

    #
    # class WebSpider:
    #     def process_item(self, item, spider):
    #         print(item)
    def close_spider(self, spider):
        fileName = "publicTriffic/result/baidu.json" if spider.name == "baidu" else "publicTriffic/result/8684.json"
        jsonFile = open(fileName, "w", encoding='utf-8')
        resultDict = {
            'busData': self.db['busData']
        }
        dump(self.db, jsonFile, ensure_ascii=False)
        jsonFile.close()
