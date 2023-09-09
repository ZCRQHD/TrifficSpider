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
        json = js.loads(response.text)


        for group in json['stations']:
            provinceName = group['c']  # item里用的
            for city in group['childs']:
                item = BusItem()
                urlName = city['e'] # 网址用的名字
                cityName = city['c'] # item里用的
                item['city'] = cityName
                item['province'] = provinceName

                yield Request("https://{}.8684.cn/".format( urlName),callback=self.cityPage,
                              meta={"item" : item,'city':urlName}
                              ,priority=10)
    def cityPage(self,response):
        """
        类型页
        :param response:
        :return:
        """
        tag = BeautifulSoup(response.text)
        meta = response.meta
        item = meta['item']
        cityName = meta['city']
        typeTag = tag.find('div', attrs={'class': "bus-layer depth w120"})\
        .find_all("div",attrs={'class':"pl10"})[2].find('div',attrs={'class':"list"}).\
            find_all("a",)
        item['typeTotal']  = len(typeTag)
        for type in typeTag:
            url = f"https://{cityName}.8684.cn" + type['href']
            yield Request(url,meta={'item':item,'city':cityName},callback=self.typePage,priority=15)

    def typePage(self,response):
        """
        公交页
        :param response:
        :return:
        """
        tag = BeautifulSoup(response.text)
        item = response.meta['item']
        cityName = response.meta['city']
        lineTag = tag.find('div',attrs={'class':"list clearfix"})
        for line in lineTag.find_all('a'):
            url = "https://{}.8684.cn/".format( cityName ) + line['href']
            item['code'] = url.split('_')[1]
            item['name'] = line.text
            yield Request(url,meta={'item':item},callback=self.linePage,priority=20)

    def linePage(self,response):
        tag = BeautifulSoup(response.text)
        item = response.meta['item']
        lineTag = tag.find_all('div',attrs={"class" : "service-area"})[1]
        upLineTag,downLineTag = lineTag.find_all("div",attrs={'class':"bus-lzlist mb15"})
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
        downLineList.reverse()
        lineList = []
        for i in range(0,len(upLineList)):
            onlyUp = False
            onlyDown = False
            if upLineList[0][2] == downLineList[0][2]:
                lineList.append((upLineList[0],'double'))
                upLineList.pop(0)
                downLineList.pop(0)
            else :
                for code in range(1,len(downLineList)):
                    """
                    遍历下行列表，如果没有说明上行站仅上行
                    """
                    if downLineList[code][2] == upLineList[0][2]:
                        """
                        说明该站非仅上行
                        """
                        lineList.append((downLineList[0],'down'))
                        downLineList.pop(0)
                        break
                else:
                    """
                    没找到的话
                    """
                    lineList.append((upLineList[0],'up'))
                    upLineList.pop(0)
        item['stationList'] = lineList
        yield item




"""
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
"""







"""

https://api.8684.cn/bus_station_map_station.php?code=5085a6b6&ecity=beijing&kind=2
https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=12.9&city=110000&geoobj=116.42275%7C39.878084%7C116.51115%7C39.973276&keywords=%E5%9C%B0%E9%93%815%E5%8F%B7%E7%BA%BF
https://ditu.amap.com/detail/get/detail?id=BV10707429

"""



