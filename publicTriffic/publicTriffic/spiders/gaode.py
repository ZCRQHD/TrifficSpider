import scrapy
import json
from scrapy import Request
class GaodeSpider(scrapy.Spider):
    name = "gaode"
    allowed_domains = ["ditu.amap.com"]
    start_urls = ["https://ditu.amap.com"]
    gaodeHeader = {'Amapuuid': 'eb9014d2-0dda-4253-83a9-b21d4755055e', 'Bx-Ua': '226!9n4T4I89blMvWbbvmsQh43rb2twZOGpzS3Pj25WTc4oJO9/uzGSHeiyvuyapcpbsQi4huOa5A3F3P1MrQkI1bpSJYWQKYBxlagxgZXk3iiXhDcndKfuX0xghn+oxdmXfqUIJJjCD5j7nqFlpKQm11wnZ/yyKeNxYrulOZHrfwPiLXOnOhX86fB3NlsQC6v0dLfv214w9+NxdLTp2JKDFTfDGOl96sMO6e1JpshJlMxgrpVo8bY9Y82/f4kHoMZ2TnmtZ6CAQn82BDQ82CyYsHWtbt62hN9/Bru/ad37/SO9mPg3oygWQWtQ9CyDyynmzwrPdwduv98SJjBsfneKrYqbyHGdpMhIME6EwiVrkAsZ8UUCFjRMdSwtXr8AEeg2/JVlP1hQP4ZQs38WqfYmhzO9W3DaHpXbZg8IMQWrCBZQs38TldmRExYqLcVw4q503nFNev/bSgjWO2zMtqcrMRWGeWAiBvhRuMY92yUafnyMuUQQLyoh5vZ2pWqiv4gv8lzy9HDoeycWDjJnC0uhzgA/pDquT5hT9lwZXnbDn/0ONDriYqUuXb9S9D/W8qbgunn4yBR5I/Duxcf5ORUcIu99Ef9kHXg0qQQe5nsUneOJ1OEQVeWD5s2l6VXbvvu59d74dBmaIbmWkVkbCgog04eKRWSves5g/+npuwUb8bhRcOMuNyohe/KY+WI54y53bnM6upmT6nuuRLBT6AnNm6mDv3gQew6zcIsfdqDEfnTTR3BTlLLw7dOCoVUazpwUoJPukttTdny5R3BQHYVccT59Dhscly0c2EH9edUJGgbnRhnuGye3VwXpbcKDGH2zBvnVDdgskMWs5kMQYqgmn/oIocID1sXbZg8l2D4IvRZ5R9+aQqIaVehMpsgbQ/lY7r6bUssUMibsPNTg0Wta8UXxKqkX3DxRENHjrJdroy0k2ql/oNgQOUfuOQRdPJrTT5zo3XyqMWKhI21jxQFEDKFnYwqMb426MK0C3GMQgX8BsLjOR1GMZHcJQ847EhvrSE2jsOZbITiV3OqNQmt8Gtk6gLXJHwN8or0cD6ftadharHnw3EpL5B82kX+4Oq0HaaazQYeLfl2fZb2hrsAcTNoTaYqysG1gcz1GFDa09m58ZXVp2bs6m58iGYAF04d9+jXc9dbtieR6dZYfzBq6OCqH+QhiyDR3p8cfYeoghGHl8gxU+a1l6JEqBRdZafycS8V/X+zOiXWI9p7wJjVZn6HM8nPx2HF0M3UTJvS4MfU50/S9tUFs9bj8oRQyM9X7fIBA3z02D1GcD2Z+Q6XUeVSl0vppJPc04ZjiPt2ZM5O9migeG2H39WNri9Ykxi1fRDclx9geY/tn31lFIjnmVExKznbdLveddiRdVPRcQ6yvi2TJL7doBCg/dVxeX5DdcdR2J13lH1TKz5BEOde7e6BqwLIgCJUwTUo0DjdeCrtrONTzpQrcmNq3LWGK+So/ZG5FIkVYwf5C6GJm+lJ1N2raOiTDoYn4uZEAD85Qadi9FbnHTnQeMsLHAuF5P4R2cisSnTltXAU6Cbu7HFux0SFvs7RFezKXPjbNy9xstj+SEOHmQWDgCpe8o29vWsylmx7/3M4ayceTuuj/zWPtYgGEFi6RrAJYLCF+dhW==', 'Bx-Umidtoken': 'G1DB414D8F394342BD21ADFF744C1EDD9985FEC5A3A6152C0CF', 'Bx-V': '2.5.3', 'Cookie': 'cna=w4HSHMbOyWwCAbfHQldAWKl3; _uab_collina=168396040077731577836503; dev_help=LPAWPeoPuYSFLKTB9ah74zI0MDZkYmYxNzZjNmQ3M2M0ODk3MDUxNDcwMmI5NTE4YWNlMWFiYzA3NDFiMWQ3MTUyYzMzODQ2MmVmZmY4MzU8Gs372zuty1O9jHIitkqbZmVQuNakusP9snMzR35Fyhh%2BJJycP8d%2BAgjXibzDp7RAgR2clk1OTQ%2BzZGMCSxlOUpwWWQBDlx39tgdznWMvpW57QD%2FHJzWT3KvWq%2FebwIc%3D; passport_login=MTI4NjU3ODI5MixhbWFwTkZXZ09uaHUscGJ1M3Bhb3k2dWk0czQ1emVpM3Mzd3NmaXp3ajN6a3ksMTY5MzAxNzQ3OSxZell6WlRKbFpXSmhORGN5WlRsaFptRXpNVFpsWVdaa05tWTJNVGxqWm1RPQ%3D%3D; guid=1aa8-4994-6eaf-d47d; xlly_s=1; x-csrf-token=b03c6c5db0eafb548e987a78e09a10f4; tfstk=db6MF64SX1RsjRdxDfp_IJ35X6Vdqd9y3-bvkEI2uhYB7tC9kx5hkwq6kiz1otYFc1E6MPimf9boHAU_1ikDHKz8y8eRfc9X3zUYLYR6t-BJely8eGs_6Pvna8E61llGACGLgsiAB4AvrmUX_iDzqXFG9eDqE0TW_vbjMjGj-hOwzByjnO7tTbzR6xtUD9ljGC-BxUUOSM8c.; l=fBIVypBPTzOl7vKNBO5aKurza77TCddj1sPzaNbMiIEGIs1KAFUkVP8IMu1ngjVR5HG5-TfbTnxzbG_pcdFk-QUdgsFuuNzdDt9AuY96-uFHzSC..; isg=BJOTY55Z8rgq1riOpLll5_aGIhe9SCcK9h_w8EW9BrLpxKBm0xmPWtNS_jSq5H8C', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76'}

    def start_requests(self):
        jsonFile = open('E:\\工程文件\\程序文件\\python项目\\公交爬虫\\publicTriffic\\busData.json','r')
        jsonDict = json.load(jsonFile)
        urlFormat = "https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=17.5&city={}&keywords={}"
        for provinceName in jsonDict['busData'].keys():
            province = jsonDict['busData'].pop(provinceName)
            for cityName in province.keys():
                city = province.pop(cityName)
                for typeName in city.keys():
                    type = city.pop(typeName)
                    for line in type:
                        url = urlFormat.format(line['city'],line['name'])
                        yield Request(url,callback=self.gaodeLineParse,priority=10,headers=self.gaodeHeader)
    def gaodeLineParse(self,response):
        self.log(response.json())