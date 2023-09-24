import scrapy
from scrapy import Request
import json
from..items import *
class BaiduSpider(scrapy.Spider):
    name = "baidu"
    allowed_domains = ["map.baidu.com"]
    start_urls = ["https://map.baidu.commap.baidu.com"]

    def start_requests(self):
        jsonFile = open('E:\\工程文件\\程序文件\\python项目\\公交爬虫\\publicTriffic\\busData.json', 'r')
        jsonDict = json.load(jsonFile)
        urlFormat = "https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd={}&c=131&src=0&wd2={}"

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
            if [903, "公交线路"] in classList:
                lineType = "bus" if 903 in classList else "subway"
                yield Request(lineUrl.format(place['uid']), callback=self.lineParse, priority=15,meta={
                    'type': lineType
                })


    def lineParse(self,response):
        lineJson = json.loads(response.text)
        lineInformathon = lineJson['content'][0]
        lineType = response.metadata['type']
        if lineType == 'bus':
            item = BusItem()
            item['name'] = lineInformathon['raw_name']
            item['code'] = lineInformathon['uid']
        elif lineType == 'subway':
            item = SubwayItem()