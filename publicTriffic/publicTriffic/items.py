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
    code = scrapy.Field()
    time = scrapy.Field()  # 运营时间
    # lineTotal = scrapy.Field() # 线路总数
    stationList = scrapy.Field()  # 站点名录
    path = scrapy.Field() #
    preOpen = scrapy.Field() # 暂缓站数

class BusItem(LineItem):
    busType = scrapy.Field()  #公交类型

    # typeTotal = scrapy.Field() # 类型总数



class SubwayItem(LineItem):
    color = scrapy.Field() # 代表色
    zhixian = scrapy.Field() #是否有支线
    zhixianList = scrapy.Field() #支线表


class Station:
    def __init__(self, name,time,location):
        self.name = name
        self.time = time
        self.location = location
class SubwayStation(Station):
    def __init__(self, name,time=None,fencha=None,huancheng=None,line=None,location=None):
        super(Station, self).__init__(name,time,location)
        self.fencha =fencha
        self.huancheng =huancheng
        self.line = line




class BusStation(Station):
    def __init__(self, name,line=None,platform=None,subway=None,time=None,location=None):
        super(BusStation, self).__init__(name,time,location )
        self.line = line  # 包含线路名
        self.subway = subway  # 地铁换乘信息
        self.platform = platform  # 站台表

class Time:
    """
    运行时间类
    """
    def __init__(self,isSeason=False,timeDict={}):
        self.isSeason = isSeason
        self.timeDict = timeDict
class TrafficWeb(scrapy.Item):
    """
    交通网
    """
    stationList = scrapy.Field()
    lineList = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()