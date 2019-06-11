import pymongo
from pymongo import MongoClient
from fifa_data.mongodb_addr import host
import json
from pprint import pprint


client = MongoClient(f'{host}', 27017)
db = client.agents_proxies
collection = db.fate0_proxy_list

FILE_NAME = '/FIFA/fifa_data/proxies/proxy_storage.json'


def get_proxies(filename):

    input_file = open(filename)
    json_array = json.load(input_file)

    return json_array


new_proxies = get_proxies(filename=FILE_NAME)

# INITIAL IMPORT

def initdb():

    init_operations = [pymongo.operations.InsertOne(
        {"ip": ip["ip"]}
    ) for ip in new_proxies]

    init_result = db.collection.bulk_write(init_operations)

    init_result

    pprint(init_result.bulk_api_result)

# SUBSEQUENT UPDATES

def updatedb():

    operations = [pymongo.operations.UpdateOne(
        filter={"ip": ip["ip"]},
        update={"$setOnInsert": {"ip": ip["ip"]}},
        upsert=True
        ) for ip in new_proxies]

    result = db.collection.bulk_write(operations)

    result
    pprint(result.bulk_api_result)


if __name__=='__main__':
    if db.user_agents.find({}).count() < 1:
        initdb()
    else:
        updatedb()
