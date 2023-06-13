import csv
import sys

from os import environ
from os import path
from dotenv import load_dotenv
import boto3
import pandas as pd

from machine_learning.content_based_filtering import summary_based_recommand
from scraping.parsing import parsing_and_insert_DB
sys.path.append("")

import threading

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from model import Novel, Member
from scraping.kakao import kakao_scraping
from scraping.munpia import munpia_scraping
from scraping.ridi import ridi_scraping
from scraping.series import series_scraping

from session import SessionLocal



app = FastAPI()


mutex = threading.Lock()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return "파이썬 서버 메인"


@app.get("/scraping")
async def scraping():

    # 락 얻으려고 시도
    # 누군가 락을 가지고 있다면 대기하지 않고 False 반환
    # 락은 한 스레드내에서 공유한다.
    # 같은 스레드라면, 여러 락을 호출해서 사용할 수 있다.
    ridi_scraping()
    kakao_scraping()
    munpia_scraping()
    series_scraping()

    # acquire = mutex.acquire(blocking=False)
    #
    # if not acquire:
    #     return {"message": "Already running."}, 400
    #
    #try:
    #        thread_ridi = threading.Thread(target=ridi_scraping)
    #        thread_munpia = threading.Thread(target=munpia_scraping)
    #        thread_kakao = threading.Thread(target=kakao_scraping)
    #        thread_series = threading.Thread(target=series_scraping)
    
    #        thread_ridi.start()
    #        thread_munpia.start()
    #        thread_kakao.start()
    #        thread_series.start()
    #
    #        thread_ridi.join()
    #        thread_munpia.join()
    #        thread_kakao.join()
    #        thread_series.join()
    
    
    #finally:
    #      mutex.release()

    # 스크래핑 끝나고 해당 파일을 S3에 올리기
    s3 = s3_connection()

    try:
        filepath = './scraping_files/'
        filenames = ['kakao.csv', 'naver.csv', 'ridi0.csv', 'ridi1.csv', 'ridi2.csv', 'munpia0.csv', 'munpia1.csv']

        for filename in filenames:
            try:
                # 파일이 존재하고, 파일 사이즈가 0보다 크면, 업로드
                if path.isfile(filepath + filename) and path.getsize(filepath + filename) > 0:

                    local_filename = filepath + filename     # 로컬에 있는 파일 이름
                    bucket_name = 'novelforumbucket'
                    bucket_filename = filename    # 버킷에 저장할 파일 이름

                    s3.upload_file(local_filename, bucket_name, bucket_filename)
                else:
                    print(filename, path.getsize(filepath + filename))

            except Exception as e:
                continue
    except Exception as e:
        print(e)



    return "ok", 200

# Depends는 fast api에서 의존성 주입에 사용되는 데코레이터
# db 변수에 get_db()로 연결하려는 DB에 대한 세션 정보를 주입할 수 있다.
@app.get('/novel')
def get_novels(db: Session = Depends(get_db)):

    # Novel model에 대한 객체 리스트 생성
    novels = db.query(Novel).all()
    return novels





@app.get('/novel/{novel_idx}')
def get_recommand(novel_idx, db: Session = Depends(get_db)):
    
    # Novel model에 대한 객체 리스트 생성
    novels = db.query(Novel).all()

    # 쿼리 결과를 딕셔너리로 변환
    novel_dicts = [novel.__dict__ for novel in novels]
    
    # 줄거리 기반 추천 호출
    result = summary_based_recommand(novel_idx, novel_dicts)

    return result


def s3_connection():
    load_dotenv()
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id="{}".format(environ['S3_ACCESS_KEY']),
            aws_secret_access_key="{}".format(environ['S3_SECRET_ACCESS_KEY']),
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3
