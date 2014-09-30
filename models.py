from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from app import db



class Result(db.Model):
    """Sqlalchemy deals model"""
    __tablename__ = "results"

    id = db.Column(Integer, primary_key=True)

    tournament_url = db.Column('tournament_url',  String)

    home_team  = db.Column('home_team',  String)
    away_team  = db.Column('away_team',  String)
    datetime = db.Column('datetime', String)
    year     = db.Column('year', String)
    league   = db.Column('league', String)
    group    = db.Column('group', String)

    event_id = db.Column('event_id', String)
    event_hash_01 = db.Column('event_hash_01', String)
    event_hash_02 = db.Column('event_hash_02', String)
    tournament_id = db.Column('tournament_id', String)

    event_results = db.Column('event_results', String)

    ou_full_results  = db.Column('ou_full_results',  String)
    ou_frst_results  = db.Column('ou_frst_results',  String)
    ou_scnd_results  = db.Column('ou_scnd_results',  String)
    hda_full_results = db.Column('hda_full_results', String)
    hda_frst_results = db.Column('hda_frst_results', String)
    hda_scnd_results = db.Column('hda_scnd_results', String)
