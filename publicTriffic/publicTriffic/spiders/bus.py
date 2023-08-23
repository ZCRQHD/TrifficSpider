import scrapy
from scrapy import Request
from ..items import *
from bs4 import BeautifulSoup
class BusSpider(scrapy.Spider):
    name = "bus"
    allowed_domains = ["www.8684.cn"]
    start_urls = ["https://api.8684.cn/v3/api.php?do=citys&act=province"]

    def parse(self, response):
        json = response.getjson()

        for group in json['stations']:
            provinceName = group['c']  # item里用的
            for city in group['childs']:
                item = BusItem()
                urlName = group['e'] # 网址用的名字
                cityName = group['c'] # item里用的
                item['city'] = cityName
                item['province'] = provinceName
                yield Request("https://{}.8684.cn/".format( urlName),callback=self.cityPage,
                              meta={"item" : item}
                              ,priority=10)
    def cityPage(self,response):
        tag = BeautifulSoup(response.text)
        meta = tag.metadata
        item = meta['item']
        typeTag = tag.find('div', attrs={'class': "bus-layer depth w120"})\
        .find_all("div",attrs={'class':"pl10"})[2].find('div',attrs={'class':"list"}).\
            find_all("a",)
        item['typeTotal']  = len(typeTag)
        for type in typeTag:
            url = type['href']
            yield Request(url,meta={'item':item},callback=self.typePage,priority=15)

    def typePage(self,response):
        pass




