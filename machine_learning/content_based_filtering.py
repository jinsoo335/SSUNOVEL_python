import csv
import re
import time

import pandas as pd


from konlpy.tag import Okt
from sentence_transformers import SentenceTransformer, util


# 전처리
def preprocessing(sentence_list):
    # 한국어 영어 숫자 제외하고 나머지는 공백으로 바꾸기
    sentence_list = [re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣0-9a-zA-Z ]', ' ', str(s)) for s in sentence_list]

    # open korean text 형태소 분석기를 사용해서 주어진 문장에서 형태소를 추출한다.
    # 추출할 떄 어간 추출도 동시에 진행해서  합니다 -> 하다로 바꾼다.
    okt = Okt()
    # hannanum = Hannanum()
    # kkma = Kkma()
    # komoran = Komoran()
    # mecab = Mecab()

    token_ko_list = [okt.morphs(s, stem=True) for s in sentence_list]

    #print(token_ko_list)

    # print(hannanum.morphs(sentence_list[0]))
    # print(kkma.morphs(sentence_list[0]))
    # print(komoran.morphs(sentence_list[0]))
    # print(mecab.nouns(sentence_list[0]))

    # 불용어 제외하기
    with open('stop_word.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    print(stop_words)

    token_list = []

    for token_ko in token_ko_list:
        temp_list = []

        for t in token_ko:
            if t not in stop_words:
                temp_list.append(t)

        token_list.append(temp_list)

    sentence_list = [' '.join(t) for t in token_list]

    return sentence_list


def summary_based_recommand(novel_idx, novel_dict):

    df = pd.DataFrame(novel_dict)

    # 시간 측정
    start_time = time.time()

    # SentenceTransformer 라이브러리를 사용하여 미리 훈련된 KR - SBERT 모델을 로드
    # 사전 훈련된 가중치를 가져와 모델을 사용할 수 있도록 준비하는 역할
    # 이미 학습된 모델을 로드하여 활용
    model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    # model = SentenceTransformer('jhgan/ko-sroberta-multitask')

    # dataframe을 리스트로 변환 (문장 리스트여야 한다.)
    sentences = df['summary'].tolist()
    # sentences = df['synopsis'].tolist()

    # 전처리
    # okt = Okt()
    pre_time = time.time()
    print("전처리 시작")
    sentences = preprocessing(sentences)
    print("전처리 끝: ", time.time() - pre_time)

    # 입력 문장을 문장 임베딩으로 인코딩
    # show_progress_bar=True로 하면 인코딩 진행상황을 보여준다.
    vectors = model.encode(sentences, show_progress_bar=True)  # encode sentences into vectors

    # 문장 벡터 간의 코사인 유사도를 계산
    # 계산된 유사도 행렬은 문장 간의 유사도를 나타내며, 각 쌍에 대한 유사도 값이 포함됨.
    similarities = util.cos_sim(vectors, vectors)  # compute similarity between sentence vectors

    # 유사도 검사에 걸린 시간 출력
    print(f"{time.time() - start_time:.4f} sec")

    num_sentences = len(sentences)
    print(num_sentences)

    f = open('test.csv', 'w', encoding="utf-8-sig", newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(['novel_idx', 'reommend_novel_idx'])

    for i in range(1, 2):

        # list(enumerate(similarities[i]))는 인덱스와 유사도의 튜플로 리스트를 만들어준다.
        test_sim_scores = list(enumerate(similarities[i]))
        test_sim_scores = sorted(test_sim_scores, key=lambda x: x[1], reverse=True)

        test_movie_indices = [i[0] for i in test_sim_scores[1:5]]

        pd.describe_option()

        print(sentences[i])

        for idx in test_movie_indices:
            print(sentences[idx], similarities[i][idx])
            print()
            datas.append(df['novel_idx'][i], df['novel_idx'][idx])

    writer.writerows(datas)
    f.close()




    return 'ok'