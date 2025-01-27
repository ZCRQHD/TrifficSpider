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
import json
x_pi = math.pi * 3000.0 / 180.0
import logging
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率

class SearchPipeline:
    def open_spider(self, spider):
        pass

    def process_item(self, item, spider: scrapy.Spider):
        if spider.name == 'baidu':
            uid = item['code']


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
        spider.log("DB pipline has started",level=logging.INFO)

    def process_item(self, item, spider: scrapy.Spider):
        if spider.name == 'baidu':
            platformList = []
            for platform in item['stationList']:

                geox, geoy = platform[1].split(',')
                lan, lot = self.convert(float(geox), float(geoy))
                platformResult = Platform.get_or_none(
                    Platform.uid == platform[0]
                )
                if platformResult is None:

                    Platform.create(
                        uid = platform[0],
                        geox=lan,
                        geoy=lot,
                        name=platform[2]
                    )
                    platformList.append(platform[0])
                    spider.log(f"successfully add platform {platform[2]} uid={platform[0]} ",)

            lineResult = Line.get_or_none(Line.uid == item['code'])
            if lineResult is None:
                startStation = item['stationList'][0][0]
                endStation = item['stationList'][-1][0]
                pathList = [self.convert(float(lan),float(lot)) for lan,lot in item['path']]
                pathStr = json.dumps(pathList)
                Line.create(
                    uid=item['code'],
                    name=item['name'],
                    pairCode=item['pairCode'],
                    preOpen=item['preOpen'],
                    province=item['province'],
                    city=item['city'],
                    startStation=startStation,
                    endStation=endStation,
                    path = pathStr,
                    company=item['company']



                )
                spider.log(f"successfully add line {item['name']} uid={item['code']} ")
            else:
                spider.log(f"{item['name']} uid={item['code']} has already existed")
            for platform_uid in platformList:

                lineStationResult = LineStation.get_or_none(
                    line=item['code'],
                    platform=platform_uid
                )
                if lineStationResult is None:
                    LineStation.create(

                        line=item['code'],
                        platform=platform_uid
                    )
                    spider.log(f"successfully connect line={item['code']} and platform={platform_uid} ")
                else:
                    spider.log(f"line={item['code']} and platform={platform_uid} has already connect")


        return item

    def close_spider(self, spider):
        db.close()
        spider.log("successfully closed database")


class SaveJsonPipeline:
    def open_spider(self, spider):
        self.db = {}

    def process_item(self, item, spider: scrapy.Spider):
        if spider.name == "bus":
            province = item['province']
            city = item['city']
            busType = item['busType']
            spider.log(f"the size of {item['province']} {item['city']} {item['name']} is {asizeof(item)}")
            if province not in self.db.keys():
                self.db[province] = {}
            if city not in self.db[province].keys():
                self.db[province][city] = {} if spider.name == 'bus' else []
            if spider.name == 'bus':
                if busType not in self.db[province][city].keys():
                    self.db[province][city][busType] = []
                self.db[province][city][busType].append(dict(item))
                spider.log("successfully append {} {} {} {}".format(province, city, item['busType'], item['name']))
            else:
                self.db[province][city].append(dict(item))
                spider.log("successfully append {} {} {}".format(province, city, item['name']))

        return item

    #
    # class WebSpider:
    #     def process_item(self, item, spider):
    #         print(item)
    def close_spider(self, spider):
        fileName = "publicTriffic/result/baidu.json" if spider.name == "baidu" else "publicTriffic/result/8684.json"
        jsonFile = open(fileName, "w", encoding='utf-8')
        resultDict = {
            'busData': self.db
        }
        dump(resultDict, jsonFile, ensure_ascii=False)
        jsonFile.close()
