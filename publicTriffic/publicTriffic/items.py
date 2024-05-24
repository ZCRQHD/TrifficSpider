# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import hashlib

class LineItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    code = scrapy.Field()  # uid
    time = scrapy.Field()  # 运营时间
    stationList = scrapy.Field()  # 站点名录
    path = scrapy.Field() #
    preOpen = scrapy.Field()  # 暂缓站数
    company = scrapy.Field()  # 运营公司
    pairCode = scrapy.Field()  # 对开车次uid
class BusItem(LineItem):
    busType = scrapy.Field()
    # typeTotal = scrapy.Field() # 类型总数



class SubwayItem(LineItem):
    color = scrapy.Field() # 代表色


class MainStation:
    """
    总站
    判定机制：省市站名均相同
    """

    def __init__(self, province, city, name):
        self.province = province
        self.city = city
        self.name = name
        self.stationList = []
        self.ID = self.getID()

    def getID(self):
        hash = hashlib.sha256(bytes(f"{self.province}/{self.city}:{self.name}"))
        return hash.hexdigest()

    def appendStation(self, station):
        if station in self.stationList:
            self.stationList.append(station)


class Platform:
    """
    站台类
    判定：位置一样
    """

    def __init__(self, location, station, uid, name):
        self.location = location  # 位置
        self.station = station  # 所属车站uid
        self.uid = uid  # 本身uid
        self.name = name  # 站名
        self.lineID = []

    def appendLine(self, line):
        if line not in self.lineID:
            self.lineID.append(line)


class Station:
    """
    车站类
    判定：uid
    """

    def __init__(self, uid):
        self.uid = uid  # 本身的uid
        self.mainStation = ""  # 总站uid
        self.platformList = []  # 站台表

    def appendPlatform(self, platform):
        if platform in self.platformList:
            self.platformList.append(platform)
