import gzip
import json
import os
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import parallel_bulk

from tqdm import tqdm

from mapping import mapping

DATA = "/run/media/martin/a2ea889e-257f-4584-9011-cac4516c42e5/pdt/"
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
        if not success:
            print("Insert failed: ", info)
        # print("insert successfull")


def preprocess_object(obj, recursive=False):
    return {
        "id": obj["id"],
        "created_at": obj["created_at"],
        "full_text": obj["full_text"],
        "entities": {
            "hashtags": list(map(lambda o: o["text"], obj["entities"]["hashtags"])),
            "user_mentions": list(
                map(lambda o: {"screen_name": o["screen_name"], "name": o["name"], "id": o["id"]},
                    obj["entities"]["user_mentions"]))
        },
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
        "retweeted_status": preprocess_object(obj["retweeted_status"]) if recursive and "retweeted_status" in obj.keys() else None
    }


def file_to_data(file):
    with gzip.open(file) as lines:
        for line in lines:
            obj = json.loads(line)
            yield preprocess_object(obj, True)


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
