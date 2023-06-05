import csv
import pandas as pd
import datatable as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import get_db
from scraping.parsing import parsing_and_insert_DB


filepath_list = ['ridi0.csv',
                 'munpia0.csv',
                 'series.csv']

DB_URL = 'mysql+pymysql://admin:00000000@database-1.cbpiwhu41l0j.ap-northeast-2.rds.amazonaws.com/NovelForumDB'


engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()


parsing_and_insert_DB(session, filepath_list)