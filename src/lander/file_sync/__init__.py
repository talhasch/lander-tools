import time
from typing import List

import requests

from lander.constants import *
from lander.db import mongo_db, pg_session_maker
from lander.logger import create_logger
from lander.model import FileCache, State

logger = create_logger('file-sync')


def get_users(min_date: int) -> List:
    filters = {'radiksType': 'BlockstackUser', 'updatedAt': {'$gt': min_date}}
    return [x for x in mongo_db['radiks-server-data'].find(filters, sort=[('updatedAt', 1)]).limit(10)]


def worker():
    session = pg_session_maker()
    state = session.query(State).filter(State.id == 1).first()
    assert state is not None

    min_date = state.min_date
    users = get_users(min_date)

    if len(users) == 0:
        session.close()
        time.sleep(0.2)
        return

    m_date = None

    for row in users:
        m_date = row['updatedAt']

        if not ('apps' in row['profile'] and APP_ORIGIN in row['profile']['apps']):
            logger.info('{}/{}: app definition not found'.format(row['username'], row['_id']))
            continue

        url = '{}{}'.format(row['profile']['apps'][APP_ORIGIN], PUBLISHED_FILE)

        try:
            contents = requests.get(url).text
        except BaseException as ex:
            logger.info('{}/{}: could not get file'.format(row['username'], row['_id']))
            continue

        # More than 1 user with same file can be exists due to https://github.com/blockstack/radiks/issues/61
        checks = session.query(FileCache).filter(FileCache.url == url).all()
        for c in checks:
            session.delete(c)
            session.flush()

        item = FileCache()
        item.url = url
        item.contents = contents
        item.updated = row['updatedAt']
        session.add(item)

        session.flush()

        # logger.info('{}/{}: ok'.format(row['username'], row['_id']))

    if m_date is not None:
        state.min_date = m_date

    session.commit()
    session.close()


def main():
    while True:
        worker()
