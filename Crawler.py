import re

import bs4
import psycopg2
import requests
import urllib.parse
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, connection):
        print("Конструктор")
        self.dbConnection: psycopg2.connection = connection
        self.cursor: psycopg2.cursor = connection.cursor()

    def __del__(self):
        print("Деструктор")
        pass

    # 1. Индексирование одной страницы
    def addIndex(self, soup, url):
        pass

    # 2. Получение текста страницы
    def getTextOnly(self, soup, wiki_flag):
        if wiki_flag:
            useful = soup.find("div", {"id": "bodyContent"})
            for item in useful.find_all("span", {"class": "mw-editsection"}):
                item.decompose()
            for item in useful.find_all('div', {'class': 'printfooter'}):
                item.decompose()
            for item in useful.find_all('div', {'class': 'catlinks'}):
                item.decompose()
            text = useful.get_text().replace('\n', ' ')
        else:
            useful = soup.find('body')
            text = useful.get_text().replace('\n', ' ')
        return text

    # 3. Разбиение текста на слова
    def separateWords(self, text):
        words = re.sub(r"[,.;:@#?!&$()\-—]+\ *", " ", text).split()
        words_clear = []
        for s in words:
            name = re.sub(r'\[[^][]*\]', '', s)
            words_clear.append(name)
        return words_clear

    # 4. Проиндексирован ли URL (проверка наличия URL в БД)
    def isIndexed(self, url) -> bool:
        return False

    # 5. Добавление ссылки с одной страницы на другую
    def addLinkRef(self, urlFrom, urlTo, linkText):
        pass

    def getUrls(self, url) -> list:
        newUrls = []
        wiki_pattern = "https?://([0-9a-z]+[.])wikipedia[.]org/.*"
        begin_url = 'https://ru.wikipedia.org'
        if re.fullmatch(wiki_pattern, url):  # Если работаем с урлом вики, то берем только ссылки с основной части
            html_doc = requests.get(url)
            soup = bs4.BeautifulSoup(html_doc.text, features="html.parser")
            useful = soup.find("div", {"id": "bodyContent"})
            for item in useful.find_all("span", {'class': 'mw-editsection'}):  # Удаляем блоки Править и Править код
                item.decompose()
            for item in useful.find_all("a", {'class': 'mw-file-description'}):  # Удаляем блоки c ссылками на картинки
                item.decompose()
            for item in useful.find_all("a", {'class': 'mw-jump-link'}):
                item.decompose()
            for item in useful.find_all('sup', {'class': 'reference'}):
                item.decompose()
            for item in useful.find_all("div", {"id": "toc"}):
                item.decompose()
            for item in useful.find_all("span", {'class': 'mw-cite-backlink'}):
                item.decompose()
            for a in useful.find_all('a', href=True):
                if re.search('/w/.*', a['href']) or re.search("index.php*", a['href']):
                    continue
                elif re.match('/wiki/.*', a['href']):
                    clearurl = begin_url + a['href']
                    newUrls.append(urllib.parse.unquote(clearurl))
                elif a['href'].startswith('/'):
                    clearurl = url + a['href']
                    newUrls.append(urllib.parse.unquote(clearurl))
                else:
                    clearurl = a['href']
                    newUrls.append(urllib.parse.unquote(clearurl))
        else:
            html_doc = requests.get(url)
            soup = bs4.BeautifulSoup(html_doc.text, features="html.parser")
            useful = soup.body
            for a in useful.find_all('a', href=True):
                newUrls.append(urllib.parse.unquote(a))
        return newUrls

    def crawl(self, urlList, maxDepth=3):
        wiki_pattern = "https?://([0-9a-z]+[.])wikipedia[.]org/.*"
        wiki_flag = False
        for currDepth in range(0, maxDepth):
            for url in urlList:
                if re.fullmatch(wiki_pattern, url) is not None:
                    wiki_flag = True
                response = requests.get(url)
                if response.status_code == 200:
                    html_text = response.text
                    soup = bs4.BeautifulSoup(html_text, features="html.parser")
                    clear_text = self.getTextOnly(soup, wiki_flag)
                    clear_words = self.separateWords(clear_text)
                    for word_id, word in enumerate(clear_words):
                        isFiltered = word.isnumeric()
                        query = """
                                DO 
                                $do$
                                BEGIN
                                    IF NOT EXISTS (select word from wordlist where word = %s) THEN
                                        INSERT into wordlist (word, isFiltered) values (%s, %s);
                                    END IF;
                                END;
                                $do$
                                """
                        self.cursor.execute(query, (word, word,  isFiltered))
                    # query = "INSERT INTO urllist (url) values (%s)"
                    # self.cursor.execute(query, url)
                    self.dbConnection.commit()

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
        print("DB structure created successfully!")

    # 8. Вспомогательная функция для получения идентификатора и
    # добавления записи, если такой еще нет
    def getEntryId(self, tableName, fieldName, value):
        return 1
