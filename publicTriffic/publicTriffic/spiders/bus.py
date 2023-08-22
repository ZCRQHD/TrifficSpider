import scrapy
from scrapy import Request
from ..items import *

class BusSpider(scrapy.Spider):
    name = "bus"
    allowed_domains = ["www.8684.cn"]
    start_urls = ["https://api.8684.cn/v3/api.php?do=citys&act=province"]

    def parse(self, response):
        json = response.getjson()
        for group in json['stations']:
            for city in group['childs']:
                urlName = group['e'] # 网址用的名字
                itemName = group['c'] # item里用的


