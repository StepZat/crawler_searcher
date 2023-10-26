import re
import psycopg2
import requests
import urllib.parse
import bs4
import matplotlib.pyplot as plt
from Crawler import Crawler
from Searcher import Searcher

if __name__ == "__main__":
    connection = psycopg2.connect(host='192.168.56.101', database='labIS', user='tester', password='tester')
    # spider = Crawler(connection)
    # spider.initDB(spider.dbConnection)
    # urlList = ["https://ru.wikipedia.org/wiki/Аэропорт", "https://ru.wikipedia.org/wiki/Нектарин"]
    # spider.crawl(urlList, 3)
    # spider.createGraphs()
    # #parent_urls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    # #child_urls = [0, 233, 306, 349, 647, 1136, 1527, 1912, 2054, 2089, 2201,  2213, 2273, 2535, 3321]
    # #plt.plot(parent_urls, child_urls)
    # #plt.title("Зависимость UrlTo от UrlFrom")
    # #plt.xlabel("Количество ссылок UrlFrom")
    # #plt.ylabel("Количество ссылок UrlTo")
    # #plt.show()
    # spider.dbConnection.close()
    searcher = Searcher(connection)
    query = "население страны"
    searcher.getSortedList(query)



