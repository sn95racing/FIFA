import random
from datetime import datetime, timedelta

from pymongo import MongoClient
from fifa_data.mongodb_addr import host


def gen_useragent_list():

    """
    Generate a list of user-agents from the user-agent database. This
    list will be used by the user-agent rotator.
    """

    client = MongoClient(host, 27017)
    db = client.agents_proxies
    collection = db.user_agents

    query = collection.find({
        'last_modified': {'$gte': datetime.utcnow() - timedelta(days=14)},
        '$and': [
            {'$or': [
                {'OS': 'Windows'},
                {'OS': 'Mac OS X'},
                {'OS': 'macOS'},
                {'OS': 'Linux'}
            ]},
            {'$or': [
                {'hardware_type': 'Computer'},
                {'hardware_type': 'Windows'},
                {'hardware_type': 'Linux'},
                {'hardware_type': 'Mac'}
            ]},
            {'$or': [
                {'popularity': 'Very common'},
                {'popularity': 'Common'}
            ]}
        ]
        },
                            {'_id': 0, 'user_agent': 1}
    )

    user_agent = [x['user_agent'] for x in query]
    random.shuffle(user_agent)
    # TODO implement warning / or break code if user agent list is empty
    # or less than a certain threshold
    print("Number of user agents pulled: ", len(user_agent))
    return user_agent


if __name__ == '__main__':
    gen_useragent_list()
