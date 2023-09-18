import re

import psycopg2
import requests
import urllib.parse
import bs4
from Crawler import Crawler


#if __name__ == "__main__":
#    connection = psycopg2.connect(host='192.168.2.72', database='labIS', user='tester', password='tester')
#    spider = Crawler(connection)
#    spider.initDB(spider.dbConnection)

base_url = 'https://ru.wikipedia.org/wiki/Аэропорт'
# begin_url = 'https://ru.wikipedia.org'
html_doc = requests.get(base_url)
soup = bs4.BeautifulSoup(html_doc.text, features="html.parser")
useful = soup.find("div",{"id":"bodyContent"})
for item in useful.find_all("span", {"class": "mw-editsection"}):
    item.decompose()
text = useful.get_text().replace('\n', ' ')
text = re.sub(r"[,.;@#?!&$()\-—]+\ *", " ", text).split()
print(text)
#for word in text:
#    print(word)
# for a in useful.find_all('a', href=True):
#     clearurl = ''
#     if re.search('/w/.*', a['href']) or re.search("index.php*", a['href']):
#         continue
#     elif re.match('/wiki/.*',  a['href']):
#         clearurl = begin_url + a['href']
#         print(urllib.parse.unquote(clearurl))
#     elif a['href'].startswith('/'):
#         clearurl = base_url + a['href']
#         print(urllib.parse.unquote(clearurl))
#     elif a['href'].startswith('http'):
#         clearurl = a['href']
#         print(urllib.parse.unquote(clearurl))
# #print(html_doc.url)
# #print(urllib.parse.unquote(html_doc.url))
# #print(html_doc.headers['content-language'] == 'ru')
# #print(html_doc.headers)
# #query = f"INSERT INTO urllist (url) VALUES ('{html_doc.url}')"
# #cursor.execute(query)
# #connection.commit()