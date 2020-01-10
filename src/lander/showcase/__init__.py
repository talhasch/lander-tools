import json
import logging
import os
from typing import List

from lander.constants import *
from lander.db import mongo_db, pg_db
from lander.util import assert_env_vars

assert_env_vars('APP_ORIGIN')

APP_ORIGIN = os.environ.get('APP_ORIGIN')

logging.basicConfig(level=logging.INFO)


def get_users() -> List:
    filters = {'radiksType': 'BlockstackUser'}
    return [x for x in mongo_db['radiks-server-data'].find(filters)]


def worker():
    users = get_users()

    for row in users:
        # ignore non-username accounts
        if row['username'] is None:
            continue

        # app definition not found
        if not ('apps' in row['profile'] and APP_ORIGIN in row['profile']['apps']):
            continue

        file_url = '{}{}'.format(row['profile']['apps'][APP_ORIGIN], PUBLISHED_FILE)

        sql = "SELECT updated, contents FROM file_cache WHERE url='{}' LIMIT 1".format(file_url)
        file_rec = pg_db.execute(sql).fetchone()

        if file_rec is None:
            continue

        try:
            data = json.loads(file_rec.contents)
            assert data['name']
        except BaseException:
            continue

        eligible = len([x for x in data['accounts'].values() if x != '']) > 1 \
                   and data['photo'] != '' \
                   and data['bg']['image'] != 'wave.jpg' \
                   and len(data['description']) > 10

        if not eligible:
            continue

        o = {
            'username': row['username'],
            'name': data['name'],
            'description': data['description'],
            'photo': data['photo'],
            'url': 'https://landr.me/{}'.format(row['username'])
        }

        print(o)
        print('----------')


def main():
    worker()
