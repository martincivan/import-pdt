import gzip
import json
import psycopg2
from psycopg2 import Error
import time

DATA = "/run/media/martin/a2ea889e-257f-4584-9011-cac4516c42e5/pdt/"

subor = DATA + "coronavirus-tweet-id-2020-08-01-05.jsonl.gz"


def spracuj_krajinu(krajina, k, db):
    if krajina is None:
        return None
    cursor = db.cursor()
    code = krajina['country_code']
    name = krajina['country']
    if code not in k.keys():
        try:
            cursor.execute("INSERT INTO countries (code, name) VALUES (%s, %s) RETURNING id", (code, name))
            k[code] = cursor.fetchone()[0]
            db.commit()
        except Error:
            pass
    return k[code]


def spracuj_hestegy(hesteg, h, db):
    cursor = db.cursor()
    result = []
    for teg in hesteg:
        text = teg['text']
        if text not in h:
            try:
                cursor.execute("INSERT INTO hashtags (value) VALUES (%s) RETURNING id", (text,))
                h[text] = cursor.fetchone()[0]
                db.commit()
            except Error as e:
                pass
        result.append(h[text])
    return result


def zapis_priradenia_hestegov(pridadenia_hestegov, db):
    cursor = db.cursor()
    cursor.executemany("INSERT INTO tweet_hashtags (tweet_id, hashtag_id) VALUES (%s, %s)", pridadenia_hestegov)
    db.commit()
    pridadenia_hestegov.clear()


def zapis_pouzivatelov(pouzivatelia, db):
    cursor = db.cursor()
    prerobeny = list(map(lambda pouzivatel: (
    pouzivatel['id'], pouzivatel['screen_name'], pouzivatel['name'], pouzivatel['description'],
    pouzivatel['followers_count'], pouzivatel['friends_count'], pouzivatel['statuses_count']), pouzivatelia))
    cursor.executemany("""INSERT INTO accounts (id, screen_name, name, description, followers_count, friends_count, statuses_count) 
    VALUES (%s, %s, %s, %s, %s, %s, %s) 
    ON CONFLICT (id)
    DO UPDATE SET screen_name=excluded.screen_name, name=excluded.name, description=excluded.description, followers_count=excluded.followers_count, friends_count=excluded.friends_count, statuses_count=excluded.statuses_count
    """, prerobeny)
    db.commit()
    pouzivatelia.clear()


def update_pouzivatelov(pouzivatelia_update, mensn, db):
    cursor = db.cursor()
    cursor.executemany("""INSERT INTO accounts (id, screen_name, name) 
    VALUES (%s, %s, %s) 
    ON CONFLICT (id)
    DO NOTHING
    """, pouzivatelia_update)
    db.commit()
    pouzivatelia_update.clear()
    cursor = db.cursor()
    cursor.executemany("""INSERT INTO tweet_mentions (account_id, tweet_id) 
    VALUES (%s, %s) 
    """, mensn)
    db.commit()
    mensn.clear()

def daj_polohu(objekt):
    try:
        if objekt['coordinates']:
            c = objekt["coordinates"]["coordinates"]
            return f"POINT({c[0]} {c[1]})"
    except (KeyError, IndexError):
        return None
    return None


def zapis_tvity(tvity, db):
    cursor = db.cursor()
    cursor.executemany("""INSERT INTO tweets (id, content, location, retweet_count, favorite_count, happened_at, author_id, country_id, parent_id) 
    VALUES (%s, %s, ST_GeomFromText(%s, 4326), %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING
    """, tvity)
    db.commit()
    tvity.clear()


def spracuj_subor(nazov_suboru, k, h, db):
    with gzip.open(nazov_suboru) as s:
        pridadenia_hestegov = []
        pouzivatelia = []
        pouzivatelia_update = []
        mensn = []
        tvity = []
        for riadok in s:
            objekt = json.loads(riadok)
            spracuj_tvit(db, h, k, mensn, objekt, pouzivatelia, pouzivatelia_update, pridadenia_hestegov, tvity)
        zapis_tvity(tvity, db)
        update_pouzivatelov(pouzivatelia_update, mensn, db)
        zapis_priradenia_hestegov(pridadenia_hestegov, db)
        zapis_pouzivatelov(pouzivatelia, db)


def spracuj_tvit(db, h, k, mensn, objekt, pouzivatelia, pouzivatelia_update, pridadenia_hestegov, tvity):
    try:
        if objekt['place'] is not None:
            pass
        objekt['krajina'] = spracuj_krajinu(objekt['place'], k, db)
    except (KeyError):
        objekt['krajina'] = None
    try:
        idecka = spracuj_hestegy(objekt['entities']['hashtags'], h, db)
        for idecko in idecka:
            pridadenia_hestegov.append((objekt['id'], idecko))
        if len(pridadenia_hestegov) > 1000:
            zapis_priradenia_hestegov(pridadenia_hestegov, db)
    except KeyError:
        pass
    pouzivatelia.append(objekt['user'])
    if len(pouzivatelia) > 1000:
        zapis_pouzivatelov(pouzivatelia, db)
    for pouzivatel in objekt['entities']['user_mentions']:
        pouzivatelia_update.append((pouzivatel['id'], pouzivatel['screen_name'], pouzivatel['name']))
        mensn.append((pouzivatel['id'], objekt['id']))
    if len(pouzivatelia_update) > 1000:
        update_pouzivatelov(pouzivatelia_update, mensn, db)
    try:
        objekt['parent'] = objekt['retweeted_status']['id']
        spracuj_tvit(db, h, k, mensn, objekt['retweeted_status'], pouzivatelia, pouzivatelia_update, pridadenia_hestegov, tvity)
    except KeyError:
        objekt['parent'] = None
    tvity.append((objekt['id'], objekt['full_text'], daj_polohu(objekt), objekt['retweet_count'],
                  objekt['favorite_count'], objekt['created_at'], objekt['user']['id'], objekt['krajina'],
                  objekt['parent']))
    if len(tvity) > 1000:
        zapis_tvity(tvity, db)


# with Manager() as manager:
# krajiny = manager.dict()
# hestegy = manager.dict()


connection = psycopg2.connect(user="postgres",
                              password="postgres",
                              host="127.0.0.1",
                              port="5432",
                              database="postgres")
krajiny = {}
hestegy = {}

start = time.time()
spracuj_subor(subor, krajiny, hestegy, connection)
print("hotovo")
end = time.time()
print(end - start)