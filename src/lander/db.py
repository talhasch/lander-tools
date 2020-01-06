import os

import pymongo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# PG

db_url = os.environ.get('DB_URL')

pg_db = create_engine(db_url)

session_args = {'autocommit': False, 'autoflush': False}

pg_session_maker = sessionmaker(bind=pg_db, **session_args)

# MONGO

client = pymongo.MongoClient(os.environ.get('MONGO_URL'))

mongo_db = client.get_default_database()
