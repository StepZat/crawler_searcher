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
    urlList = ["https://ru.wikipedia.org/wiki/Аэропорт", "https://ru.wikipedia.org/wiki/Нектарин"]
    #spider.crawl(urlList,2)
    spider.createGraphs()
    spider.dbConnection.close()



