from sqlalchemy import (Column, String, Integer, BigInteger)
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['FileCache', 'State', ]

Base = declarative_base()


class FileCache(Base):
    __tablename__ = 'file_cache'

    url = Column('url', String, nullable=False, primary_key=True)

    updated = Column('updated', BigInteger, nullable=False)

    contents = Column('contents', String, nullable=False, primary_key=True)


class State(Base):
    __tablename__ = 'state'

    id = Column('id', Integer, nullable=False, primary_key=True)

    min_date = Column('min_date', BigInteger)
