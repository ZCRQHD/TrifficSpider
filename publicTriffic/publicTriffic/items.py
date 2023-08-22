# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LineItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    city = scrapy.Field()
    busType = scrapy.Field()
    time = scrapy.Field()  # 运营时间
    stationList = scrapy.Field()  # 站点名录

