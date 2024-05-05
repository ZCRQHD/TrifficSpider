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


class BaiduSpider(scrapy.Spider):
    name = "baidu"
    allowed_domains = ["map.baidu.com"]
    start_urls = ["https://map.baidu.commap.baidu.com"]

    def start_requests(self):
        jsonFile = open('E:\\工程文件\\程序文件\\python项目\\公交爬虫\\publicTriffic\\busData.json', 'r',
                        encoding="utf-8")
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
                yield Request(lineUrl.format(uid), callback=self.lineParse, priority=5, meta={
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
        self.log(f"found {lineType} line in {item['province']} {item['city']} named {item['name']}")
        pathStr:str = content['geo']
        pathStr = pathStr.split("|")[2][:-1]
        pathList = pathStr.split(",")
        convertPathList = []
        for i in range(0, len(pathList) - 1, 2):
            lan ,lot = float(pathList[i]),float(pathList[i + 1])
            position = (lan, lot)
            convertPathList.append(position)
        item['path'] = convertPathList
        stationList = [(station['uid'], station['geo'].split("|")[1], station['name'])
                       for station in content['stations']]
        item['stationList'] = stationList
        if lineType == 'subway':
            item['color'] = content['line_color']

        for station in stationList:
            if station[0] not in self.stationSet:
                self.stationSet.add(station[0])
                url = f"https://map.baidu.com/?uid={station[0]}&ugc_type=3&ugc_ver=1&qt=detailConInfo&device_ratio=2&compat=1&t=1714795401159&auth=bf6H8U7K2IFHGd@x@5VeC6B0Xbf=5HC4uxNxENTHBTRtyOOyyIFIAUvCuyAT9xXwvkGcuVtvvhguVtvyheuVtvCMGuVtvCQMuVtvIPcuxtw8wkv7uvZgMuVtv@vcuVtvc3CuVtvcPPuVtveGvuxVtEnrR1GDdw8E62qvyMuJx7OIgHvhgMuzVVtvrMhuzVtGccZcuxtf0wd0vyOyFOUICUy&seckey=6cm9oCWblWcXJH0b4zVSMCw/zCVTeM6PwLZ6AwxhTtOXbc4JhCaIUuGhXM3GdiGSVrIeM0WWKTAXL2nEuexD5w==,6cm9oCWblWcXJH0b4zVSMCw_zCVTeM6PwLZ6AwxhTtPtxDiQY_xf54N3FJhucp5GGHOByJ6fEHfcjUqr7h8GZmHDi1rcUs1YhedmiJPShVNbacxRGMhFMrTNXpjaBXOkAXmClDAJRybwqL2Xk-Q5f1W7da-MW97xRlJMgxuYRd9C8fT5C8EOxGYpBGON-go4GStjrJRLQBinQFo7O3mlcA&pcevaname=pc4.1&newfrom=zhuzhan_webmap"
                yield Request(url=url, callback=self.stationParse, priority=20, meta={})

        yield item

    def stationParse(self, response):
        stationJson = json.loads(response.text)
        meta = response.request.meta
        for station in stationJson['content']:
            typeList = [type for type in station['cla']]
            if 22 in typeList:
                for line in station['blinfo']:
                    if line['uid'] not in self.lineSet:
                        lineUrl = "https://map.baidu.com/?qt=bsl&tps=&newmap=1&uid={}&c=131"
                        uid = line['uid']
                        self.lineSet.add(uid)

                        lineType = "bus" if 214 in typeList else "subway"
                        yield Request(lineUrl.format(uid), callback=self.lineParse, priority=5, meta={
                            'type': lineType
                        })





