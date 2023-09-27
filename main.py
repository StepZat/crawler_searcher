import re

import psycopg2
import requests
import urllib.parse
import bs4
from Crawler import Crawler

if __name__ == "__main__":
    connection = psycopg2.connect(host='192.168.56.101', database='labIS', user='tester', password='tester')
    spider = Crawler(connection)
    #spider.initDB(spider.dbConnection)
    urlList = ["https://ru.wikipedia.org/wiki/Аэропорт"]
    test = spider.getUrls(urlList[0])
    for item in test:
        print(item)
    #print(len(spider.getUrls(urlList[1])))
    #print(spider.isIndexed(urlList[0]))
    #spider.crawl(urlList,2)
    #print(spider.getUrls(urlList[0]))
    spider.dbConnection.close()



