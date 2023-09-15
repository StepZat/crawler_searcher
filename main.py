import re

import psycopg2
import requests
import urllib.parse
import bs4
#connection = psycopg2.connect(host='192.168.2.72',
#                              database='labIS',
#                              user='tester',
#                              password='tester')

#cursor = connection.cursor()

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
#for item in tables:
#    cursor.execute(f"DROP TABLE IF EXISTS {item} CASCADE ")
#cursor.execute(create_wordlist_query)
#cursor.execute(create_urllist_query)
#cursor.execute(create_wordlocation_query)
#cursor.execute(create_linkbetweenurl_query)
#cursor.execute(create_linkWord_query)
#connection.commit()


base_url = 'https://ru.wikipedia.org/wiki/Аэропорт'
begin_url = 'https://ru.wikipedia.org'
html_doc = requests.get(base_url)
soup = bs4.BeautifulSoup(html_doc.text, features="html.parser")
useful = soup.find("div",{"id":"bodyContent"})
for item in useful.find_all("span", {"class": "mw-editsection"}):
    item.decompose()
for a in useful.find_all('a', href=True):
    clearurl = ''
    if re.search('/w/.*', a['href']) or re.search("index.php*", a['href']):
        continue
    elif re.match('/wiki/.*',  a['href']):
        clearurl = begin_url + a['href']
        print(urllib.parse.unquote(clearurl))
    elif a['href'].startswith('/'):
        clearurl = base_url + a['href']
        print(urllib.parse.unquote(clearurl))
    elif a['href'].startswith('http'):
        clearurl = a['href']
        print(urllib.parse.unquote(clearurl))
#print(html_doc.url)
#print(urllib.parse.unquote(html_doc.url))
#print(html_doc.headers['content-language'] == 'ru')
#print(html_doc.headers)
#query = f"INSERT INTO urllist (url) VALUES ('{html_doc.url}')"
#cursor.execute(query)
#connection.commit()