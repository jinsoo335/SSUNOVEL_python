import sys
sys.path.append("")

from os import environ

from dotenv import load_dotenv
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker


# .env 파일에서 환경 설정 정보 가져오기
load_dotenv()


DB_URL = 'mysql+pymysql://{}:{}@{}/{}'.format(
    environ['DB_USER'],
    environ['DB_PASSWORD'],
    environ['DB_HOST'],
    environ['DB_NAME']
)


engine = create_engine(DB_URL)