import re
import psycopg2
import requests
import urllib.parse
import bs4
import matplotlib.pyplot as plt
from Crawler import Crawler
from Searcher import Searcher
from htmlgen import get_colored_html

if __name__ == "__main__":
    connection = psycopg2.connect(host='192.168.56.101', database='labIS', user='tester', password='tester')
    #spider = Crawler(connection)
    #spider.initDB(spider.dbConnection)
    #urlList = ["https://ru.wikipedia.org/wiki/Кустарник", "https://ru.wikipedia.org/wiki/Нектарин"]
    #spider.crawl(urlList, 3)
    #spider.dbConnection.close()
    searcher = Searcher(connection)
    query = "растения россии"
    searcher.getSortedList(query)
    #get_colored_html("https://ru.wikipedia.org/wiki/Лес", "растения россии")



