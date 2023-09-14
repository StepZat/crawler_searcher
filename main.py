import psycopg2

connection = psycopg2.connect(host='192.168.2.72',
                              database='labIS',
                              user='tester',
                              password='tester')

cursor = connection.cursor()

create_wordlist_query = ("CREATE TABLE IF NOT EXISTS wordlist ("
                         "rowID integer PRIMARY KEY,"
                         "word text,"
                         "isFiltered bool)")

create_urllist_query = ("CREATE TABLE IF NOT EXISTS urllist ("
                        "rowID integer PRIMARY KEY,"
                        "url TEXT)")

create_wordlocation_query = ("CREATE TABLE IF NOT EXISTS wordlocation ("
                             "rowID integer PRIMARY KEY,"
                             "fk_wordID integer REFERENCES wordlist (rowID),"
                             "fk_URLID integer REFERENCES urllist (rowid) ,"
                             "location integer)")

create_linkbetweenurl_query = ("CREATE TABLE IF NOT EXISTS linkbetweenURL ("
                               "rowID integer PRIMARY KEY, "
                               "fk_fromURL_ID integer REFERENCES urllist (rowid),"
                               "fk_toURL_ID integer REFERENCES urllist (rowid))")

create_linkWord_query = ("CREATE TABLE IF NOT EXISTS linkWord ("
                         "rowID integer PRIMARY KEY,"
                         "fk_wordID integer REFERENCES wordlist (rowid),"
                         "fk_linkID integer REFERENCES linkbetweenurl (rowid))")
tables = ["wordlist", "urllist", "wordlocation", "linkbetweenURL", "linkWord"]
for item in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {item} CASCADE ")
cursor.execute(create_wordlist_query)
cursor.execute(create_urllist_query)
cursor.execute(create_wordlocation_query)
cursor.execute(create_linkbetweenurl_query)
cursor.execute(create_linkWord_query)
connection.commit()
