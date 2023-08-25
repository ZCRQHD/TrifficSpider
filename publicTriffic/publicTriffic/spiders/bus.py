import scrapy
from scrapy import Request
from ..items import *
from bs4 import BeautifulSoup
class BusSpider(scrapy.Spider):
    name = "bus"
    allowed_domains = ["www.8684.cn"]
    start_urls = ["https://api.8684.cn/v3/api.php?do=citys&act=province"]

    def parse(self, response):
        """
        城市
        :param response:
        :return:
        """
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
        """
        类型页
        :param response:
        :return:
        """
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
        """
        公交页
        :param response:
        :return:
        """
        tag = BeautifulSoup(response.text)
        item = response.metadata['item']
        lineTag = tag.find('div',attrs={'class':"list clearfix"})
        for line in lineTag.find_all('a'):
            url = line['href']
            item['code'] = url.split('_')[1]
            item['name'] = line.text
            yield Request(url,meta={'item':item},callback=self.linePage,priority=20)

    def linePage(self,response):
        pass

"""

https://api.8684.cn/bus_station_map_station.php?code=5085a6b6&ecity=beijing&kind=2

https://ditu. amap.com/service/poiBus?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=9.14&city=%E4%B8%8A%E6%B5%B7%E5%B8%82&src=mypage&callnative=0&platform=pc&innersrc=uriapi&keywords=%E5%9C%B0%E9%93%813%E5%8F%B7%E7%BA%BF&data_type=BUSLINE
https://ditu.amap.com/detail/get/detail?id=BV10707429

"""



