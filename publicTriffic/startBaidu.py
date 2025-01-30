from scrapy import cmdline

cityList = []
while True:
    city = input('please input a city which you want to download,press OK to finish')
    if city == "OK":
        break
    else:
        cityList.append(city)
cityStr = ','.join(cityList)
cmdline.execute(f"scrapy crawl baidu -s TARGET_CITY={cityStr}".split())
