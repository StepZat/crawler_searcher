import re

import psycopg2
import requests
import urllib.parse
import bs4
from Crawler import Crawler

if __name__ == "__main__":
    connection = psycopg2.connect(host='192.168.56.101', database='labIS', user='tester', password='tester')
    spider = Crawler(connection)
    spider.initDB(spider.dbConnection)
    urlList = ["https://ru.wikipedia.org/wiki/Аэропорт", "https://ru.wikipedia.org/wiki/Нектарин"]
    #urlList = ["https://web.archive.org/web/20070315100833/http://www.abakan.de/info/travel/index_en.php"]
    #test = spider.getUrls(urlList[0])
    #for item in test:
    #    print(item)
    #print(len(spider.getUrls(urlList[1])))
    #print(spider.isIndexed(urlList[0]))
    #text = requests.get(urlList[0]).headers['content-type']
    #print(text.startswith('text/html'))
    spider.crawl(urlList,2)
    #print(spider.getUrls(urlList[0]))
    spider.dbConnection.close()



