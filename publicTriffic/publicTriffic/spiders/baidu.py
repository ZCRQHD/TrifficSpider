from scrapy import Request
import json
from..items import *
import json

from scrapy import Request

from ..items import *
from datetime import date
import re
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



    def lineParse(self,response):
        lineJson = json.loads(response.text)
        lineInformathon = lineJson['content'][0]
        lineType = response.metadata['type']
        if lineType == 'bus':
            item = BusItem()


        else:
            item = SubwayItem()
            color = lineInformathon['lineColor']

        item['name'] = lineInformathon['raw_name']
        item['code'] = lineInformathon['uid']
        pathStr = lineInformathon['geo'].spilt('|')[-1]
        positionList = pathStr.spilt(",")
        pathList = []
        for i in range(0, len(positionList), 2):
            pathList.append((positionList[i], positionList[i + 1]))
        stationList = lineInformathon['stations']
        item['company'] = lineInformathon['company']
        item['pairCode'] = lineInformathon['pair_line']['uid']

        # if len(lineInformathon['workTime']) == 1:
        #     time.isSeason = False
        # else:
        #     time.isSeason = True
        #     seasonTimeList = lineInformathon['workTimeDesc']
            # reText = ""
            #  for i in seasonTimeList:

        typeStr = "-公交车站" if lineType == "bus" else "-地铁站"
        stationIndex = 0
        stationName = ""
        while True:
            stationName = stationList[stationIndex]['name']
            if stationName not in self.stationSet:
                break

            else:
                stationIndex += 1
        yield Request(url="https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd={}{}&c=148&src=0&wd2=&pn=0&sug=0&l=19".format
        (stationName,typeStr)
                      ,meta={
                "station" : 0,
                "stationJson" : stationList,
                "stationList" : [],
                "item" :item
            })


    def stationParse(self,response):
        lineJson = json.loads(response.text)

