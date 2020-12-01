import gzip
import json
import os
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import parallel_bulk

from tqdm import tqdm

from mapping import mapping

DATA = "/run/media/martin/a603269a-a5d0-40eb-8191-cb1daaa1df8e/home/martin/PDT/"
INDEX = "twindex_1"


def create_actions(generator):
    for i in generator:
        yield {
            "_index": INDEX,
            "_id": i["id"],
            "_source": i
        }


def process_file(file):
    for success, info in parallel_bulk(Elasticsearch(), create_actions(file_to_data(file=file)), request_timeout=60):
        if not success or info["index"]["status"] not in (200, 201):
            print("Insert failed: ", info)
        # print("insert successfull")


def preprocess_object(obj):
    return [{
        "id": obj["id_str"],
        "created_at": obj["created_at"],
        "full_text": obj["full_text"],
        "hashtags": list(map(lambda o: o["text"], obj["entities"]["hashtags"])),
        "user_mentions": list(
            map(lambda o: {"screen_name": o["screen_name"], "name": o["name"], "id": o["id"]},
                obj["entities"]["user_mentions"])),
        "coordinates": obj["coordinates"]["coordinates"] if obj["coordinates"] is not None else None,
        "source": obj["source"],
        "in_reply_to_status_id": obj["in_reply_to_status_id"],
        "retweet_count": obj["retweet_count"],
        "favorite_count": obj["favorite_count"],
        "user": {
            "id": obj["user"]["id"],
            "name": obj["user"]["name"],
            "screen_name": obj["user"]["screen_name"],
            "description": obj["user"]["description"],
            "followers_count": obj["user"]["followers_count"],
            "statuses_count": obj["user"]["statuses_count"],
            "friends_count": obj["user"]["friends_count"],
            "created_at": obj["user"]["created_at"]
        },
        "parent_id": obj["retweeted_status"]["id"] if "retweeted_status" in obj.keys() else None
    }] + (preprocess_object(obj["retweeted_status"]) if "retweeted_status" in obj.keys() else [])


def file_to_data(file):
    global celkom
    with gzip.open(file) as lines:
        pocet = 0
        for line in lines:
            obj = json.loads(line)
            for result in preprocess_object(obj):
                pocet +=1
                yield result
    print("Pocet: " + str(pocet))
    celkom += pocet

celkom = 0
if __name__ == "__main__":
    es = Elasticsearch()
    try:
        es.indices.delete(index=INDEX)
        print("zmazane")
    except NotFoundError:
        print("nezmazane")
    es.indices.create(index=INDEX, body=mapping)

    for i in tqdm(os.listdir(DATA), ascii=True):
        print("file: " + DATA + i)
        process_file(DATA + i, )
    # pool.close()
    # pool.join()
    print("Celkom: " + str(celkom))
