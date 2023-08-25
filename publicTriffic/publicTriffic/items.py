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
    code =  scrapy.Field()
    lineTotal = scrapy.Field() # 线路总数
    stationList = scrapy.Field()  # 站点名录

class BusItem(LineItem):
    busType = scrapy.Field()  #公交类型
    time = scrapy.Field()  # 运营时间
    typeTotal = scrapy.Field() # 类型总数

################################

class SubwayItem(LineItem):
    color = scrapy.Field() # 代表色
    zhixian = scrapy.Field() #是否有支线
    zhixianList = scrapy.Field() #支线表


class Station:
    def __init__(self, name,):
        self.name = name

class SubwayStation(Station):
    def __init__(self, name,time,fencha,huancheng,line,exitList):
        super(Station, self).__init__(name)
        self.time = time
        self.fencha =fencha
        self.huancheng =huancheng
        self.line = line
        self.exitList = exitList



class BusStation(Station):
    def __init__(self, name,line,subway,platform):
        super(BusStation, self).__init__(name)
        self.line = line  # 包含线路名
        self.subway = subway  # 地铁换乘信息
        self.platform = platform  # 站台表

class TrafficWeb(scrapy.Item):
    """
    交通网
    """
    stationList = scrapy.Field()
    lineList = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()