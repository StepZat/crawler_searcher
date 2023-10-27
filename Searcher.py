import re
import bs4
import psycopg2
import requests
import urllib.parse
import matplotlib.pyplot as plt


class Searcher:
    def __init__(self, connection):
        print("Конструктор")
        self.dbConnection: psycopg2.connection = connection
        self.cursor: psycopg2.cursor = connection.cursor()

    def __del__(self):
        print("Деструктор")

    def getWordsIds(self, queryString: str) -> list:
        queryString = queryString.lower()
        queryWordlist = queryString.split(" ")
        rowidList = list()
        for word in queryWordlist:
            sql = "SELECT rowid FROM wordlist WHERE word = %s LIMIT 1"
            self.cursor.execute(sql, (word,))
            result_row = self.cursor.fetchone()
            if result_row is not None:
                word_rowid = result_row[0]
                rowidList.append(word_rowid)
                print("  ", word, word_rowid)
            else:
                raise Exception("Одно из слов поискового запроса не найдено:" + word)
        return rowidList

    def getMatchRows(self, queryString: str) -> tuple:
        # Разбить поисковый запрос на слова по пробелам
        queryString = queryString.lower()
        # получить идентификаторы искомых слов
        wordsidList = self.getWordsIds(queryString)

        # Созать переменную для полного SQL-запроса
        sqlFullQuery = (f"SELECT w0.fk_urlid urlid, w0.location w0_loc, w1.location w1_loc "
                        f"FROM wordlocation w0 "
                        f"INNER JOIN wordlocation w1 on w0.fk_urlid=w1.fk_urlid "
                        f"WHERE w0.fk_wordid={wordsidList[0]} AND w1.fk_wordid={wordsidList[1]} "
                        f"order by urlid, w0_loc, w1_loc limit 100")

        print(sqlFullQuery)
        self.cursor.execute(sqlFullQuery)
        rows = self.cursor.fetchall()
        return rows, wordsidList

    def normalizeScores(self, scores, smallIsBetter=0):
        resultDict = dict()
        vsmall = 0.00001
        minscore = min(scores.values())
        maxscore = max(scores.values())
        for (key, val) in scores.items():
            if smallIsBetter:
                resultDict[key] = float(minscore) / max(vsmall, val)
            else:
                resultDict[key] = float(val) / maxscore
        return resultDict

    def frequencyScore(self, rowsLoc):
        elem = rowsLoc[0][0]
        freqRanks = {}
        w0_locs = set()
        w1_locs = set()
        for item in rowsLoc:
            if item[0] == elem:
                w0_locs.add(item[1])
                w1_locs.add((item[2]))
            else:
                freqRanks[elem] = len(w0_locs) * len(w1_locs)
                w0_locs.clear()
                w1_locs.clear()
                elem = item[0]
                w0_locs.add(item[1])
                w1_locs.add((item[2]))
        freqRanks[elem] = len(w0_locs) * len(w1_locs)
        return self.normalizeScores(freqRanks, smallIsBetter=0)

    def getSortedList(self, query):
        rowsLoc, wordsidlist = self.getMatchRows(query)
        rawRank = self.frequencyScore(rowsLoc)
        sortedRank = dict(sorted(rawRank.items(), key=lambda x: x[1], reverse=True))
        rawPageRank = self.calculatePageRank()
        sortedPageRank = dict(sorted(rawPageRank.items(), key=lambda x: x[1], reverse=True))
        for item in rowsLoc:
            print(item)
        usedPageRank = {}
        meanRank = {}
        for key in sortedRank:
            usedPageRank[key] = sortedPageRank[key]
            meanRank[key] = (sortedRank[key] + sortedPageRank[key]) / 2
        print(sortedRank)
        print(usedPageRank)
        print(meanRank)

    def calculatePageRank(self, iterations=5):
        self.cursor.execute('DROP TABLE IF EXISTS pagerank')
        self.cursor.execute("""CREATE TABLE  IF NOT EXISTS  pagerank(
                                rowid SERIAL PRIMARY KEY,
                                url_id INTEGER,
                                score REAL
                            );""")

        self.cursor.execute("DROP INDEX   IF EXISTS wordidx;")
        self.cursor.execute("DROP INDEX   IF EXISTS urlidx;")
        self.cursor.execute("DROP INDEX   IF EXISTS wordurlidx;")
        self.cursor.execute("DROP INDEX   IF EXISTS urltoidx;")
        self.cursor.execute("DROP INDEX   IF EXISTS urlfromidx;")
        self.cursor.execute('CREATE INDEX IF NOT EXISTS wordidx       ON wordlist(word)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS urlidx        ON urllist(url)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS wordurlidx    ON wordlocation(fk_wordid)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS urltoidx      ON linkBetweenUrl(fk_tourl_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS urlfromidx    ON linkBetweenUrl(fk_fromurl_id)')
        self.cursor.execute("DROP INDEX   IF EXISTS rankurlididx;")
        self.cursor.execute('CREATE INDEX IF NOT EXISTS rankurlididx  ON pagerank(url_id)')
        self.cursor.execute("REINDEX INDEX wordidx;")
        self.cursor.execute("REINDEX INDEX urlidx;")
        self.cursor.execute("REINDEX INDEX wordurlidx;")
        self.cursor.execute("REINDEX INDEX urltoidx;")
        self.cursor.execute("REINDEX INDEX urlfromidx;")
        self.cursor.execute("REINDEX INDEX rankurlididx;")

        # в начальный момент ранг для каждого URL равен 1
        self.cursor.execute('INSERT INTO pagerank (url_id, score) SELECT rowid, 1.0 FROM urllist')
        self.dbConnection.commit()
        self.cursor.execute("SELECT * FROM urllist")
        urlList = self.cursor.fetchall()

        for i in range(iterations):
            for elem in urlList:
                print("Обработка ссылки")
                print(elem)
                pr = 0.15
                # Находи все ссылки которые ссылаются на текущую.
                self.cursor.execute(f"SELECT * from linkBetweenUrl WHERE fk_tourl_id = {elem[0]}")
                urlListTo = self.cursor.fetchall()

                if len(urlListTo) == 1 and urlListTo[0][1] is None:
                    self.cursor.execute(f"UPDATE pagerank SET score = {pr} WHERE url_id = {elem[0]}")
                    self.dbConnection.commit()
                    continue
                cList = list()
                for urlTo in urlListTo:
                    # Подсчет количества ссылок на которые ссылается urlTo
                    if urlTo[1] is not None:
                        self.cursor.execute(f"SELECT count(fk_fromurl_id) from linkBetweenUrl WHERE fk_fromurl_id = '{urlTo[1]}'")
                        c = self.cursor.fetchall()
                        cList.append(c)

                # Найти весь все ссылок

                rangeList = list()
                for elem2 in urlListTo:
                    if elem2[1] is not None:
                        self.cursor.execute(f"SELECT score FROM pagerank WHERE url_id = {elem2[1]}"),
                        rangeTmp = self.cursor.fetchall()

                        rangeList.append(rangeTmp)

                countPR = 0

                for i in range(len(rangeList)):
                    tmp = float(rangeList[i][0][0]) / float(cList[i][0][0])
                    countPR = countPR + tmp

                rangeLink = (1 - pr) + pr * countPR

                self.cursor.execute(f"UPDATE pagerank SET score = {rangeLink} WHERE url_id = {elem[0]}")
                self.dbConnection.commit()

        self.cursor.execute("SELECT url_id, score FROM pagerank")
        dictValues = self.cursor.fetchall()

        return self.normalizeScores(dict(dictValues), smallIsBetter=0)









