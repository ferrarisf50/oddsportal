from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


def create_deals_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class Result(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "results_03"

    id = Column(Integer, primary_key=True)

    tournament_url = Column('tournament_url', String)

    home_team = Column('home_team', String)
    away_team = Column('away_team', String)
    datetime  = Column('datetime',  String)
    year      = Column('year',      String)
    league    = Column('league',    String)
    group     = Column('group',     String)

    event_id = Column('event_id', String)
    event_hash_01 = Column('event_hash_01', String)
    event_hash_02 = Column('event_hash_02', String)
    tournament_id = Column('tournament_id', String)

    event_results    = Column('event_results', String)

    ou_full_results  = Column('ou_full_results',  String)
    ou_frst_results  = Column('ou_frst_results',  String)
    ou_scnd_results  = Column('ou_scnd_results',  String)
    hda_full_results = Column('hda_full_results', String)
    hda_frst_results = Column('hda_frst_results', String)
    hda_scnd_results = Column('hda_scnd_results', String)