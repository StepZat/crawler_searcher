import requests
import urllib.parse
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, connection):
        print("Конструктор")
        self.dbConnection = connection

    def __del__(self):
        print("Деструктор")
        pass

    # 1. Индексирование одной страницы
    def addIndex(self, soup, url):
        pass

    # 2. Получение текста страницы
    def getTextOnly(self, text):
        return ""

    # 3. Разбиение текста на слова
    def separateWords(self, text):
        return ""

    # 4. Проиндексирован ли URL (проверка наличия URL в БД)
    def isIndexed(self, url):
        return False

    # 5. Добавление ссылки с одной страницы на другую
    def addLinkRef(self, urlFrom, urlTo, linkText):
        pass

    # 6. Непосредственно сам метод сбора данных.
    # Начиная с заданного списка страниц, выполняет поиск в ширину
    # до заданной глубины, индексируя все встречающиеся по пути страницы
    def crawl(self, urlList, maxDepth=1):
        pass

    # 7. Инициализация таблиц в БД
    def initDB(self, conn):
        print("Создать пустые таблицы с необходимой структурой")
        create_wordlist_query = ("CREATE TABLE IF NOT EXISTS wordlist ("
                                 "rowID serial PRIMARY KEY,"
                                 "word text,"
                                 "isFiltered bool)")

        create_urllist_query = ("CREATE TABLE IF NOT EXISTS urllist ("
                                "rowID serial PRIMARY KEY,"
                                "url TEXT)")

        create_wordlocation_query = ("CREATE TABLE IF NOT EXISTS wordlocation ("
                                     "rowID serial PRIMARY KEY,"
                                     "fk_wordID integer REFERENCES wordlist (rowID),"
                                     "fk_URLID integer REFERENCES urllist (rowid) ,"
                                     "location integer)")

        create_linkbetweenurl_query = ("CREATE TABLE IF NOT EXISTS linkbetweenURL ("
                                       "rowID serial PRIMARY KEY, "
                                       "fk_fromURL_ID integer REFERENCES urllist (rowid),"
                                       "fk_toURL_ID integer REFERENCES urllist (rowid))")

        create_linkWord_query = ("CREATE TABLE IF NOT EXISTS linkWord ("
                                 "rowID serial PRIMARY KEY,"
                                 "fk_wordID integer REFERENCES wordlist (rowid),"
                                 "fk_linkID integer REFERENCES linkbetweenurl (rowid))")

        tables = ["wordlist", "urllist", "wordlocation", "linkbetweenURL", "linkWord"]
        cursor = conn.cursor()
        for item in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {item} CASCADE ")
        cursor.execute(create_wordlist_query)
        cursor.execute(create_urllist_query)
        cursor.execute(create_wordlocation_query)
        cursor.execute(create_linkbetweenurl_query)
        cursor.execute(create_linkWord_query)
        conn.commit()
        conn.close()
        print("DB structure created successfully!")

    # 8. Вспомогательная функция для получения идентификатора и
    # добавления записи, если такой еще нет
    def getEntryId(self, tableName, fieldName, value):
        return 1

