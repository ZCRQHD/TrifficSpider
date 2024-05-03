# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


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
    pass
    # typeTotal = scrapy.Field() # 类型总数



class SubwayItem(LineItem):
    color = scrapy.Field() # 代表色


class Station:
    def __init__(self, name,time,location,line,city=None):
        self.name = name
        self.time = time
        self.location = location
        self.line = line# 包含线路名
        self.city = city
class SubwayStation(Station):
    def __init__(self, name,time=None,fencha=None,huancheng=None,line=None,location=None,city=None):
        super(Station, self).__init__(name,time,location,line,city)
        self.fencha =fencha
        self.huancheng =huancheng





class BusStation(Station):
    def __init__(self, name,line=None,platform=None,subway=None,time=None,location=None,city=None):
        super(BusStation, self).__init__(name,time,location ,line,city)

        self.subway = subway  # 地铁换乘信息
        self.platform = platform  # 站台表

# class Time:
#     """
#     运行时间类
#     """
#     def __init__(self,isSeason=False,timeDict={}):
#         self.isSeason = isSeason
#         self.timeDict = timeDict
class Platform:
    """
    站台类
    """
    def __init__(self,station,location,):
        self.station = station
        self.location = location
        self.lineLIst = []
class PassStation:
    """
    经过的车站
    """
    def __init__(self,city,name,location):
        self.city = city
        self.name = name
        self.location = location
class TrafficWeb(scrapy.Item):
    """
    交通网
    """
    stationList = scrapy.Field()
    lineList = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()