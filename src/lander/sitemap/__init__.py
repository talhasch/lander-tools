import json
from datetime import datetime
from typing import List
import os

from lander.constants import *
from lander.db import mongo_db, pg_db
from lander.logger import create_logger
from lander.util import assert_env_vars

assert_env_vars('SITEMAP_OUTPUT_PATH', 'APP_ORIGIN')

APP_ORIGIN = os.environ.get('APP_ORIGIN')

logger = create_logger('sitemap')


def get_users() -> List:
    filters = {'radiksType': 'BlockstackUser'}
    return [x for x in mongo_db['radiks-server-data'].find(filters)]


def worker():
    url_list = []
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

        page_url = '{}/{}'.format(APP_ORIGIN, row['username'])

        # convert from js timestamp
        ts = file_rec.updated / 1000
        last_mod = datetime.fromtimestamp(ts).isoformat()

        url_list.append({'url': page_url, 'last_mod': last_mod})

    url_temp = '<url><loc>{}</loc><lastmod>{}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>'
    str_urls = ''.join([url_temp.format(x['url'], x['last_mod']) for x in url_list])

    doc_temp = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{}</urlset>'
    output = doc_temp.format(str_urls)

    save_path = os.environ.get('SITEMAP_OUTPUT_PATH')
    with open(save_path, 'w') as f:
        f.write(output)
        f.close()

    logger.info('Sitemap created to {}'.format(save_path))


def main():
    worker()
