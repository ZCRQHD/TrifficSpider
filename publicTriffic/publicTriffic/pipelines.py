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
            result = Line.select().where(Line.id == item['code'])
            if len(result) == 0:
                Line.create(
                    id=item['code'],
                    name=item['name'],
                    pairCode=item['pairCode'],
                    preOpen=item['preOpen'],
                    province=item['province'],
                    city=item['city'],
                    company=item['company']
                )
                spider.log("succcessfully save line {} id={} to datatbase".format(item['name'], item['code']))
            for platform in item['stationList']:
                hashResult = hashlib.sha256(bytes(platform[1].encode()))
                platform_uid = hashResult.hexdigest()
                station_uid = platform[0]
                hashResult = hashlib.sha256(
                    bytes(",".join([item['province'], item['city'], item["name"]]).encode())
                )
                mainStation_uid = hashResult.hexdigest()

                try:
                    MainStation.create(
                        province=item['province'],
                        city=item['city'],
                        name=platform[2],
                        id=mainStation_uid

                    )
                except IntegrityError:
                    spider.log(f"main station named{platform[2]} uid={mainStation_uid} has already exists")

                try:
                    Station.create(
                        id=platform[0],
                        mainStation=mainStation_uid
                    )
                except IntegrityError:
                    spider.log(f"station named{platform[2]} uid={station_uid} has already exists")
                lan, lot = platform[1].split(',')
                geox, geoy = self.convert(float(lan), float(lot))
                try:

                    Platform.create(
                        id=platform_uid,
                        geox=geox,
                        geoy=geoy,
                        station=platform[0]

                    )
                    spider.log("succcessfully save platform {} id={} to datatbase".format(
                        platform[2], platform_uid))
                except IntegrityError:
                    spider.log(f"platform named{platform[2]} uid={platform_uid} at {geox},{geoy} has already exists")
                del lan, lot, geox, geoy
                try:
                    LineStation.create(
                        line=item['code'],
                        platform=platform_uid
                    )
                except IntegrityError as e:
                    spider.log(e)

            try:
                pathList = [
                    tuple([item['code']] + self.convert(float(lan), float(lot))) for lan, lot in item['path']
                ]
                Path.insert_many(pathList, fields=[Path.line, Path.geox, Path.geoy])
            except IntegrityError as e:
                spider.log(e)
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
        dump(self.db, jsonFile, ensure_ascii=False)
        jsonFile.close()
