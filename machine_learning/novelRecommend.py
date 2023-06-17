import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from surprise import SVD
from surprise import Dataset
from surprise import accuracy
from surprise.dataset import DatasetAutoFolds
from surprise import Reader
from dotenv import load_dotenv
from os import environ
import time


def sort_est(pred):
    return pred.est


# 파라미터로 들어오는 유저 id가 읽지 않는 소설 리스트를 반환한다
def get_unread_novel(review, userId):
    # 입력값으로 들어온 userId에 해당하는 사용자가 평점을 매긴 모든 도서를 리스트로 생성
    read_novel = review[review['user_idx'] == userId]['novel_idx'].tolist()
    print(read_novel)

    # 모든 소설 번호를 list로 변환
    # 라뷰 데이터셋에는 소설 번호가 중복으로 되어있으므로 하나씩만 나오게 한다 .
    total_novels = np.unique(review['novel_idx']).tolist()

    # 모든 소설 id 중 읽은 소설을 제외한 소설들을 가져온다.
    unread_novels = [novel for novel in total_novels if novel not in read_novel]
    # print('평점 매긴 도서 수 : ', len(read_novel), '추천 대상 도서 수 : ', len(unread_novels), '전체 도서 수 : ', len(total_novels))

    return unread_novels


def connectDB(DB_URL):
    return create_engine(DB_URL)

# 추천 시스템 알고리즘 시작
# 파라미터 모델, 추천받고자 하는 사용자 번호, 추천받고자 하는 사용자가 읽지 않은 소설, 몇 개까지 추천할 것인지
def recommend_novel_using_surprise(model, userId, unread_novels, top_n=10):
    # 읽지 않는 소설에 대해 각 예상 평점을 계산한다.
    # prediction 객체는 user_id, novel_id, est (예상 평점)을 가진다.
    predictions = [model.predict(str(userId), str(item)) for item in unread_novels]

    # sortkey_est() 반환값의 내림 차순으로 정렬 수행하고 top_n개의 최상위 값 추출.
    predictions.sort(key=sort_est, reverse=True)
    top_predictions = predictions[:top_n]
    #print(top_predictions)

    # top_n으로 추출된 영화의 정보 추출, 영화 아이디, 추천 예상 평점
    top_book_ids = [int(pred.iid) for pred in top_predictions]
    top_book_rating = [pred.est for pred in top_predictions]

    # 탑 10개의 예상 평점, 해당 평점의 소설 번호를 튜플의 형태로 저장한다.
    top_book_preds = [(id, rating) for id, rating in
                      zip(top_book_ids, top_book_rating)]
    return top_book_preds




def loadDummyData(engine, user_id):  # 더미데이터를 이용한 추천 시스템
    """
    현재 사이트에 리뷰를 달 수 없어서 user_id에 해당하는 리뷰를 가져오는 건 패스하고 임의로 유저 번호를 넘겨서 추천하도록 함.
    리뷰를 달 수 있게 되면 아래 주석을 해제.
    """
    info = pd.read_sql(f"select member_idx as user_idx, novel_idx, rating from review where review.member_idx = {user_id}", engine)  # 추천 대상 리뷰 읽어오기
    dummy = None

    dummy = pd.read_sql("select user_idx, novel_idx, rating from ridi", engine)  # Load Dummy Data;
    dummy = dummy.groupby('user_idx').filter(lambda x: len(x) >= 5)
    result = pd.concat([info,dummy])

    return result


# review 테이블 가져오기 -> 정제가 필요함. 추후 수정 작업 진행할 예정..
def loadData(engine):
    return pd.read_sql("select member_idx as user_idx, novel_idx, rating from review ", engine)


def recommendation(user_id: int):
    load_dotenv()

    DB_URL = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(
        environ['DB_USER'],
        environ['DB_PASSWORD'],
        environ['DB_HOST'],
        environ['DB_NAME']
    )

    engine = connectDB(DB_URL)  # db 연결

    print('start recommend : user_id=', user_id)

    if user_id == 9999:  # 더미 데이터 가져오기
        #print('get dummy data..')
        df = loadDummyData(engine, user_id)
    else:
        #print('not dummy user!')
        df = loadData(engine)  # 학습을 위한 df 가져오기

    df.to_csv('ForParsing.csv', encoding='UTF-8', index=None, header=None)

    # Surprise를 이용한 행렬 분해 방식의 추천 시스템
    reader = Reader(line_format='user item rating', sep=',', rating_scale=(0, 5))
    data = Dataset.load_from_file('ForParsing.csv', reader=reader)
    trainset = data.build_full_trainset()  # 모든 데이터를 학습용으로 쓴다.

    # SVD를 이용한 학습진행.
    model = SVD()
    model.fit(trainset)

    unread_novels = get_unread_novel(df, user_id)

    # 추천 받은 novel_id 저장
    recommend = recommend_novel_using_surprise(model, user_id, unread_novels)
    recommend_id = [r[0] for r in recommend]

    # print(recommend_id) #추천 받은 id 출력

    engine.dispose()  # db 연결 해제
    print('추천 리스트 : ', recommend_id)

    return recommend_id  # 추천하는 소설 id 리턴
