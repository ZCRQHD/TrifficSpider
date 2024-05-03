from scrapy import Request
from..items import *
import json

from scrapy import Request
from scrapy.http.response import Response
import math
from ..items import *
from datetime import date
import re
import bd09convertor
x_pi = math.pi  * 3000.0 / 180.0

a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率

class BaiduSpider(scrapy.Spider):
    name = "baidu"
    allowed_domains = ["map.baidu.com"]
    start_urls = ["https://map.baidu.commap.baidu.com"]

    def start_requests(self):
        jsonFile = open('E:\\工程文件\\程序文件\\python项目\\公交爬虫\\publicTriffic\\busData.json', 'r')
        jsonDict = json.load(jsonFile)
        urlFormat = "https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd={}&c=131&src=0&wd2={}"
        self.lineSet = set()
        self.stationSet = set()
        # 这两个是去重用的
        for provinceName in jsonDict['busData'].keys():
            province = jsonDict['busData'].pop(provinceName)
            for cityName in province.keys():
                city = province.pop(cityName)
                for typeName in city.keys():
                    type = city.pop(typeName)
                    for line in type:
                        url = urlFormat.format(line['name'], line['city'])
                        yield Request(url, callback=self.searchParse, priority=10, )
    def searchParse(self, response):
        searchJson = json.loads(response.text)
        lineUrl = "https://map.baidu.com/?qt=bsl&tps=&newmap=1&uid={}&c=131"
        targetLine = searchJson['content']

        for place in targetLine:
            classList = [i[0] for i in place['cla']]
            if 904 in classList:
                lineType = "bus"
            elif 905 in classList:
                lineType = "subway"
            else :
                continue
            uid = place['uid']
            if uid not in self.lineSet:
                self.lineSet.add(uid)
                yield Request(lineUrl.format(uid), callback=self.lineParse, priority=15, meta={
                    'type': lineType
                })
            else:
                continue

    def lineParse(self,response:Response):
        """
        解析线路信息
        :param response:
        :return:
        """
        lineJson = json.loads(response.text)
        meta = response.request.meta
        lineType = meta['type']
        content = lineJson['content'][0]
        item = BusItem() if lineType == 'bus' else SubwayItem()
        item['city'] = lineJson['current_city']['name']
        item['province'] = lineJson['current_city']['up_province_name']
        item['name'] = content['name']
        item['code'] = content['uid']
        item['time'] = content['workingTimeDesc']
        item['company'] = content['company']
        item['preOpen'] = content['pre_open']
        item['pairCode'] = content['pair_line']['uid']
        pathStr:str = content['geo']
        pathStr = pathStr.split("|")[2][:-1]
        pathList = pathStr.split(",")
        convertPathList = []
        for i in range(0,len(pathList)):
            lan ,lot = float(pathList[i]),float(pathList[i + 1])
            position = self.bd09_to_gcj02(lan,lot)
            convertPathList.append(position)
        item['path'] = convertPathList
        stationList = [(station['uid'],station['geo'],station['name'])
                       for station in content['stationList']]
        item['stationList'] = stationList
        if lineType == 'subway':
            item['color'] = content['line_color']




    def bd09_to_gcj02(self,bd_lon, bd_lat):
        """
       百度坐标系(BD-09)转火星坐标系(GCJ-02)
       百度——>谷歌、高德
       :param bd_lat:百度坐标纬度
       :param bd_lon:百度坐标经度
       :return:转换后的坐标列表形式
       """
        bd_lon,bd_lat = bd09convertor.convertMC2LL(bd_lon,bd_lat)
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return gg_lng, gg_lat


    def stationParse(self,response):
        lineJson = json.loads(response.text)

