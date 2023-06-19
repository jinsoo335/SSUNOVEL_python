import csv
import re
import time
from os import environ

import pandas as pd
import numpy as np
import pymysql
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util


# 전처리
def preprocessing(sentence_list):

    # 소괄호 통째로 제거 : 소괄호의 사용처가 외래어의 영문 표기 및 한자 표기가 주를 이루기 때문에 글자 채로 제거한다.
    sentence_list = [re.sub(r'\([^)]*\)', '', s) for s in sentence_list]

    # 특정 공백이 \xa0 형식으로 나오기에 통일성을 위해서 공백으로 변경
    sentence_list = [re.sub('\xa0', ' ', s) for s in sentence_list]

    # ▶ 작가 소개 뒤로는 작가 소개가 쭉 나온다. (주로 로멘스 작품에 이런 경향이 나온다.)
    sentence_list = [re.sub(r'▶ 작가 소개.*', '', s) for s in sentence_list]

    # <작품> ~ ~~작가의 신작
    # 『작품』~ ~~작가의 신작
    # [작품] ~ ~~작가의 신작
    sentence_list = [re.sub(r'<.*?>*?작가[.!?]', '', s) for s in sentence_list]
    sentence_list = [re.sub(r'[.*?]*?작가[.!?]', '', s) for s in sentence_list]
    sentence_list = [re.sub(r'『.*?』*?작가[.!?]', '', s) for s in sentence_list]

    # 공모전 수상 내용 제거
    sentence_list = [re.sub(r'\[*?공모전 수상작\]', '', s) for s in sentence_list]

    # [단행본] 제거
    sentence_list = [re.sub(r'\[단행본\]', '', s) for s in sentence_list]

    # [합본] 제거
    sentence_list = [re.sub(r'\[합본\]', '', s) for s in sentence_list]

    # [연재] 제거
    sentence_list = [re.sub(r'\[연재\]', '', s) for s in sentence_list]

    # [독점] 제거
    sentence_list = [re.sub(r'\[독점*?\]', '', s) for s in sentence_list]

    # [완결] 제거
    sentence_list = [re.sub(r'\[완결\]', '', s) for s in sentence_list]

    # [외전 선공개] 제거
    sentence_list = [re.sub(r'\[외전 선공개\]', '', s) for s in sentence_list]

    # 해시태그 제거
    sentence_list = [re.sub(r'#([^#\s]+)\s*', '', s) for s in sentence_list]

    # ▶책 속에서 제거 : 간혹 줄거리 소개할 때, 이 문장이 처음에 들어 있는 경우가 있다.
    sentence_list = [re.sub(r'\[▶ 책 속에서\]', '', s) for s in sentence_list]

    return sentence_list


def recommend_csv_to_DB():
    load_dotenv()

    DB_URL = 'mysql+pymysql://{}:{}@{}/{}'.format(
        environ['DB_USER'],
        environ['DB_PASSWORD'],
        environ['DB_HOST'],
        environ['DB_NAME']
    )

    # CSV 파일 읽기
    datas = pd.read_csv('preprocessing_kr_category_title.csv')

    print(datas.columns)

    # pymysql 커넥션
    conn = pymysql.connect(host=environ['DB_HOST'],
                           user=environ['DB_USER'],
                           password=environ['DB_PASSWORD'],
                           db=environ['DB_NAME'])

    # 커서 열기
    cursor = conn.cursor()

    # 기존 데이터 삭제
    del_query = 'delete from recommend_novel'

    # 삭제 쿼리 실행
    cursor.execute(del_query)

    # 변경사항 커밋
    conn.commit()

    # 쿼리
    query = 'insert into recommend_novel (origin_novel_idx, recommend_novel_idx) values (%s, %s)'

    datas['ori_novel_idx'] = pd.to_numeric(datas['ori_novel_idx'])
    datas['rec_novel_idx'] = pd.to_numeric(datas['rec_novel_idx'])

    # 데이터를 리스트 안의 튜플 형태로
    selected_cols  = ['ori_novel_idx', 'rec_novel_idx']
    data = [tuple(row) for row in datas[selected_cols].to_records(index=False)]

    # 쿼리 실행
    cursor.executemany(query, data)

    # 변경사항 커밋
    conn.commit()

    # 커넥션 끊기
    conn.close()




def summary_based_recommand(novel_dict):

    df = pd.DataFrame(novel_dict)

    # SentenceTransformer 라이브러리를 사용하여 미리 훈련된 KR - SBERT 모델을 로드
    # 사전 훈련된 가중치를 가져와 모델을 사용할 수 있도록 준비하는 역할
    # 이미 학습된 모델을 로드하여 활용
    #embedder = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    embedder = SentenceTransformer('jhgan/ko-sroberta-multitask')

    # dataframe을 리스트로 변환 (문장 리스트여야 한다.)
    df['combine'] = df['summary'] + '. ' + df['title'] + '.'
    sentences = df['combine'].tolist()

    # 전처리
    print("전처리")
    sentences = preprocessing(sentences)

    # 임베딩 및 유사도 측정
    # 임베딩 - 자연어를 넥터로 바꾼 결과 or 과정 전체

    # 유사도를 저장할 파일 생성
    f = open('preprocessing_kr_category_title.csv', 'w', encoding='utf-8-sig', newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(['ori_novel_idx', 'rec_novel_idx', 'origin_sentence', 'rec_sentence', 'sim_score'])

    sentences = preprocessing(sentences)

    corpus_embeddings = embedder.encode(sentences, show_progress_bar=True)

    similarities = util.cos_sim(corpus_embeddings, corpus_embeddings)

    for i in range(len(sentences)):

        # i번째 문장의 유사도 점수
        similarity_scores = similarities[i]

        # 텐서를 numpy로 변환
        similarity_scores = np.array(similarity_scores)

        # 오름차순 인덱스로 변환
        idx = np.argsort(similarity_scores)

        # 역순으로 변환해서 내림차순 처리
        idx_list = idx[::-1]

        # 처음에는 자기 자신이 나오니까 제외
        for idx in idx_list[1:11]:
            datas.append(
                [df['novel_idx'][i], df['novel_idx'][idx], sentences[i], sentences[idx], similarity_scores[idx]])

    writer.writerows(datas)
    f.close()

    recommend_csv_to_DB()

    return 'ok'