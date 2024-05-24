import scrapy
from scrapy import Request
from ..items import *
from bs4 import BeautifulSoup
import json as js
class BusSpider(scrapy.Spider):
    name = "bus"
    allowed_domains = ["8684.cn"]
    start_urls = ["https://api.8684.cn/v3/api.php?do=citys&act=province"]

    def parse(self, response):
        """
        城市
        :param response:
        :return:
        """
        json = js.loads(str(response.text))


        for group in json['stations']:
            provinceName = group['c']  # item里用的
            for city in group['childs']:
                urlName = city['e'] # 网址用的名字
                cityName = city['c'] # item里用的

                yield Request("https://{}.8684.cn/".format( urlName),callback=self.cityPage,
                              meta={"cityItem": cityName, "province": provinceName, 'cityUrl': urlName}
                              , priority=20)
    def cityPage(self,response):
        """
        类型页
        :param response:
        :return:
        """
        tag = BeautifulSoup(str(response.text), 'lxml')
        meta = response.meta
        cityItem = meta['cityItem']
        provinceName = meta['province']
        cityName = meta['cityUrl']
        typeTagList = tag.find('div', attrs={'class': "bus-layer depth w120"})\
        .find_all("div",attrs={'class':"pl10"})
        typeTag = []
        for type in typeTagList:
            if type.find('span',attrs={'class':"kt"}).text == "线路分类：":
                typeTag = type.find_all('a')
        for type in typeTag:
            url = f"https://{cityName}.8684.cn" + type['href']
            bustype = type.text
            yield Request(url, meta={"cityItem": cityItem, "province": provinceName, 'busType': bustype
                , 'cityUrl': cityName}, callback=self.typePage, priority=30)

    def typePage(self,response):
        """
        公交页
        :param response:
        :return:
        """
        tag = BeautifulSoup(str(response.text), 'lxml')
        meta = response.meta
        cityName = meta['cityUrl']
        lineTag = tag.find('div',attrs={'class':"list clearfix"})
        for line in lineTag.find_all('a'):
            item = BusItem()
            item['province'] = meta['province']
            item['city'] = meta['cityItem']
            item["busType"] = meta['busType']
            url = "https://{}.8684.cn/".format( cityName ) + line['href']
            item['code'] = url.split('_')[1]
            item['name'] = line.text
            # self.log("get {} {} {} {}".format(item['province'], item['city'],item['busType'],item['name']))
            yield Request(url,meta={'item':item},callback=self.linePage,priority=40)

    def linePage(self,response):
        tag = BeautifulSoup(str(response.text), 'lxml')
        item = response.meta['item']
        lineTag = tag.find_all('div',attrs={"class" : "service-area"})[1]
        lineTagList = lineTag.find_all("div",attrs={'class':"bus-lzlist mb15"})
        if len(lineTagList) == 2:
            upLineTag ,downLineTag = lineTagList
            upLineList = []
            downLineList = []
            code = 0
            for i in upLineTag.find_all('a'):
                upLineList.append((code,i.text,i['href'].split("_")[1]))
                code += 1
            code = 0
            for i in downLineTag.find_all('a'):
                downLineList.append((code,i.text,i['href'].split("_")[1]))
                code += 1

            item['stationList'] = (upLineList, downLineList)
        elif len(lineTagList) == 1:
            lineList = []

            code = 0
            for i in lineTagList[0].find_all('a'):
                lineList.append(((code,i.text,i['href'].split("_")[1]),"double"))
                code += 1
            item['stationList'] = lineList
        yield item


"""

https://api.8684.cn/bus_station_map_station.php?code=5085a6b6&ecity=beijing&kind=2
https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=12.9&city=110000&geoobj=116.42275%7C39.878084%7C116.51115%7C39.973276&keywords=%E5%9C%B0%E9%93%815%E5%8F%B7%E7%BA%BF
https://ditu.amap.com/detail/get/detail?id=BV10707429

"""



