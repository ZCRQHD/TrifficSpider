# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import scrapy
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from .items import MainStation, Station, Platform
import hashlib
import bd09convertor
import math

x_pi = math.pi * 3000.0 / 180.0

a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率
class PublictrifficSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider: scrapy.Spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            if spider.name == "baidu":
                if is_item(i):
                    platList = 0
                    for plat in i['stationList']:
                        # 创建/索引站台类
                        hashResult = hashlib.sha256(plat[1].join(","))
                        platform_uid = hashResult.hexdigest()
                        if platform_uid not in self.platformDict.keys():
                            lan, lot = plat[1].split(',')
                            location = self.bd09_to_gcj02(float(lan), float(lot))
                            platform = Platform(location, plat[0], platform_uid, plat[2])
                            platform.appendLine(plat[0])
                            self.platformDict[platform_uid] = platform
                            self.platformDigit += 1
                        else:
                            platform = self.platformDict[platform_uid]
                            platform.appendLine(plat[0])
                        platList.append(self.platformDict[platform_uid])

                    i['stationList'] = platList
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
        self.mainStationDigit = 0  # 总站计数
        self.stationDigit = 0
        self.platformDigit = 0
        self.mainStationDict = {}
        self.stationDict = {}
        self.platformDict = {}

    def bd09_to_gcj02(self, bd_lon, bd_lat):
        """
       百度坐标系(BD-09)转火星坐标系(GCJ-02)
       百度——>谷歌、高德
       :param bd_lat:百度坐标纬度
       :param bd_lon:百度坐标经度
       :return:转换后的坐标列表形式
       """
        bd_lon, bd_lat = bd09convertor.convertMC2LL(bd_lon, bd_lat)
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return gg_lng, gg_lat

class PublictrifficDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
