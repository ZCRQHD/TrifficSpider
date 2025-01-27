import logging
import shelve

import json

from scrapy import Request, Spider
from scrapy.http.response import Response
import os
from ..items import *


class BaiduSpider(scrapy.Spider):
    name = "baidu"
    allowed_domains = ["map.baidu.com"]
    start_urls = ["https://map.baidu.commap.baidu.com"]
    targetCity = ["秦皇岛"]
    targetCityCode = []

    def start_requests(self):

        jsonFile = open("publicTriffic/result/8684.json", 'r',
                        encoding="utf-8")
        jsonDict = json.load(jsonFile)
        urlFormat = "https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd={}&src=0&c={}"
        self.db = {
            'line': [],
            'station': []
        }
        codeJson = open('publicTriffic/spiders/cityCode.json', encoding="utf-8")
        self.code = json.load(codeJson)
        for cityName in self.targetCity:
            self.targetCityCode.append(self.code[cityName])


        # 这两个是去重用的
        for line in jsonDict:
            if line['city'] not in self.targetCity:
                continue
            url = urlFormat.format(line['name'], self.code[line['city']])
            yield Request(url, callback=self.searchParse, priority=5, meta={
                'name': line['name'],
                'province': line['province'],
                'city': line['city']
            })

    def close(self, reason: str):
        pass

    def searchParse(self, response: Response):
        searchJson = json.loads(response.text)
        cityCode = searchJson['current_city']['code']
        lineUrl = ("https://map.baidu.com/?qt=bsl&tps=&newmap=1&uid={}&c={}&gsign=a2f7723340d3f70225ecb5222306caa8&"
                   "pcevaname=pc4.1&newfrom=zhuzhan_webmap")
        targetLine = searchJson['content']
        meta = response.request.meta
        for place in targetLine:
            classList = [i[0] for i in place['cla']]
            if 904 in classList:
                lineType = "bus"
            elif 905 in classList:
                lineType = "subway"
            else:
                continue
            uid = place['uid']
            if uid not in self.db['line']:
                self.db['line'].append(uid)
                print(self.db['line'])
                self.log("successfully search {} {} {} . uid={}".format(
                    meta['province'], meta['city'], meta['name'], uid), level=logging.INFO)
                yield Request(lineUrl.format(uid, cityCode), callback=self.lineParse, priority=10, meta={
                    'type': lineType,
                    "province": meta['province'],
                    'city': meta['city']
                })
            else:
                self.log("the line which id is {}  has been crawled".format(uid)
                         , level=logging.INFO)

    def lineParse(self, response: Response):
        """
        解析线路信息
        :param response:
        :return:
        """
        lineJson = json.loads(response.text)
        meta = response.request.meta
        lineType = meta['type']
        # 检查线路是否在爬取范围内
        if lineJson['current_city']['code'] not in self.targetCityCode:
            yield
        content = lineJson['content'][0]
        item = BusItem() if lineType == 'bus' else SubwayItem()
        item['city'] = meta['city']
        item['province'] = meta['province']
        item['name'] = content['name']
        item['code'] = content['uid']
        item['time'] = content['workingTimeDesc']
        item['company'] = content['company']
        item['preOpen'] = content['pre_open']
        item['pairCode'] = content['pair_line']['uid'] \
            if content['pair_line'] is not None else None

        self.log(f"found {lineType} line in {item['province']} {item['city']} named {item['name']}")
        pathStr: str = content['geo']
        pathStr = pathStr.split("|")[2][:-1]
        pathList = pathStr.split(",")
        convertPathList = []
        for i in range(0, len(pathList) - 1, 2):
            lan, lot = pathList[i], pathList[i + 1]
            position = (lan, lot)
            convertPathList.append(position)
        item['path'] = convertPathList
        stationList = [(station['uid'], station['geo'].split("|")[2][:-1]  # 你个百度，好好的路径不写，非得来这出，贱不贱啊~
                        , station['name'],)
                       for station in content['stations']]
        item['stationList'] = stationList
        if lineType == 'subway':
            item['color'] = content['line_color']
        self.log(
            "find {}, province={},city={},name={}.the number of station is {}".format(
                item['code'], item['province'], item['city'], item['name'], len(item['stationList'])
            ),
            level=logging.INFO
        )
        for station in stationList:
            if station[0] not in self.db['station']:
                self.db['station'].append(station[0])
                print(self.db['station'])
                url = f"https://map.baidu.com/?uid={station[0]}&ugc_type=3&ugc_ver=1&qt=detailConInfo&device_ratio=2&compat=1&t=1714795401159&auth=bf6H8U7K2IFHGd@x@5VeC6B0Xbf=5HC4uxNxENTHBTRtyOOyyIFIAUvCuyAT9xXwvkGcuVtvvhguVtvyheuVtvCMGuVtvCQMuVtvIPcuxtw8wkv7uvZgMuVtv@vcuVtvc3CuVtvcPPuVtveGvuxVtEnrR1GDdw8E62qvyMuJx7OIgHvhgMuzVVtvrMhuzVtGccZcuxtf0wd0vyOyFOUICUy&seckey=6cm9oCWblWcXJH0b4zVSMCw/zCVTeM6PwLZ6AwxhTtOXbc4JhCaIUuGhXM3GdiGSVrIeM0WWKTAXL2nEuexD5w==,6cm9oCWblWcXJH0b4zVSMCw_zCVTeM6PwLZ6AwxhTtPtxDiQY_xf54N3FJhucp5GGHOByJ6fEHfcjUqr7h8GZmHDi1rcUs1YhedmiJPShVNbacxRGMhFMrTNXpjaBXOkAXmClDAJRybwqL2Xk-Q5f1W7da-MW97xRlJMgxuYRd9C8fT5C8EOxGYpBGON-go4GStjrJRLQBinQFo7O3mlcA&pcevaname=pc4.1&newfrom=zhuzhan_webmap"
                yield Request(url=url, callback=self.stationParse, priority=20,
                              meta={'uid': station[0],
                                    'province': meta['province'],
                                    'city': meta['city']
                                    })
            else:
                self.log("the station which id is {}  has been crawled".format(station[0])
                         , level=logging.INFO)
        yield item

    def stationParse(self, response):
        stationJson = json.loads(response.text)
        meta = response.request.meta
        station = stationJson['content']
        if stationJson['current_city']['code'] not in self.targetCityCode:
            yield
        typeList = [stationType[0] for stationType in station['cla']]
        if 22 in typeList:
            lineCount = 0
            for line in station['blinfo']:
                uid = line['uid']
                if uid not in self.db['line']:
                    lineCount += 1
                    lineUrl = "https://map.baidu.com/?qt=bsl&tps=&newmap=1&uid={}&c=131"
                    province = stationJson['current_city']
                    self.db['line'].append(uid)

                    lineType = "bus" if 214 in typeList else "subway"
                    self.log("successfully add  line={} from station={}".format(uid, station['name']))
                    yield Request(lineUrl.format(uid), callback=self.lineParse, priority=10, meta={
                        'type': lineType,
                        'province': meta['province'],
                        'city': meta['city']

                    })
                else:
                    self.log("station={} line={} has already exists".format(station['name'], uid))
            self.log("successfully find station={},the number of line is {}".format(station['name'], lineCount),
                     level=logging.INFO)
        else:
            self.log("don't find station,uid={}".format(meta['uid']), level=logging.INFO)
