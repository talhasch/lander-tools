import json
from datetime import datetime
from typing import List
import os

from lander.constants import *
from lander.db import mongo_db, pg_db
from lander.logger import create_logger
from lander.util import assert_env_vars

assert_env_vars('OUTPUT_PATH')

logger = create_logger('sitemap')


def get_users() -> List:
    filters = {'radiksType': 'BlockstackUser'}
    return [x for x in mongo_db['radiks-server-data'].find(filters)]


def worker():
    users = get_users()
    url_list = []

    for row in users:

        # ignore non-username accounts
        if row['username'] is None:
            continue

        if not ('apps' in row['profile'] and APP_ORIGIN in row['profile']['apps']):
            logger.info('{}/{}: app definition not found'.format(row['username'], row['_id']))
            continue

        url = '{}{}'.format(row['profile']['apps'][APP_ORIGIN], PUBLISHED_FILE)

        sql = "SELECT updated, contents FROM file_cache WHERE url='{}' LIMIT 1".format(url)
        file = pg_db.execute(sql).fetchone()

        if file is None:
            continue

        try:
            data = json.loads(file.contents)
            assert data['name']
        except BaseException:
            continue

        page_url = '{}/{}'.format(APP_ORIGIN, row['username'])

        # convert from js timestamp
        last_mod = datetime.fromtimestamp(file.updated / 1000).isoformat()

        url_list.append({'url': page_url, 'last_mod': last_mod})

    url_temp = '<url><loc>{}</loc><lastmod>{}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>'
    str_urls = ''.join([url_temp.format(x['url'], x['last_mod']) for x in url_list])

    doc_temp = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{}</urlset>'
    output = doc_temp.format(str_urls)

    with open(os.environ.get('OUTPUT_PATH'), 'w') as f:
        f.write(output)
        f.close()

    logger.info('Sitemap created')


def main():
    worker()
