import csv
import pandas as pd
from sqlalchemy.orm import Session
import tqdm

from model import Novel, FavoriteAuthor, Author

'''
'title', 'is_complite', 'genre', 'author', 'synopsis', 'price', 'total_episode', 'comment', 'img_link','novel_link','tags'
'''


def create_alert(title, url, favorite_authors, author_idx, insert_alert_list):

    for favorite_author in favorite_authors:
        # 즐겨찾기로 등록한 작가가 맞는지 확인
        if favorite_author[1] == author_idx:
            insert_alert_list.append(title, 0, url, favorite_author[2], 'AUTHOR')


def parsing_and_insert_DB(db : Session, filepath_list):

    novels = db.query(Novel).all()
    favorite_authors = db.query(FavoriteAuthor).all()
    authors = db.query(Author).all()

    novel_dicts = [novel.__dict__ for novel in novels]
    favorite_author_dicts = [favorite_author.__dict__ for favorite_author in favorite_authors]
    author_dicts = [author.__dict__ for author in authors]

    novel_df = pd.DataFrame(novel_dicts)
    favorite_author_df = pd.DataFrame(favorite_author_dicts)
    author_df = pd.DataFrame(author_dicts)

    novel_datas = novel_df.values.tolist()
    favorite_author_datas = favorite_author_df.values.tolist()
    author_datas = author_df.values.tolist()

    #print(novel_datas)
    #print(favorite_author_datas)
    #print(author_datas)

    insert_novel_list = []
    update_novel_list = []
    insert_author_list = []
    insert_alert_list = []

    insert_novel_query = 'insert into novel(title, ' \
                         '                  summary, ' \
                         '                  cover_image, ' \
                         '                  episode, ' \
                         '                  price,' \
                         '                  download_cnt,' \
                         '                  author_idx,' \
                         '                  rating,' \
                         '                  review_cnt,' \
                         '                  category,' \
                         '                  is_finished,' \
                         '                  is_ridi,' \
                         '                  is_nvaer,' \
                         '                  is_kakao,' \
                         '                  is_munpia ) ' \
                         'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

    insert_author_query = 'insert into author(name) values (%s)'


    # 소설 정보 CSV파일을 돌면서 경로 찾기
    for filepath_idx in tqdm(range(len(filepath_list))):
        filepath = '../scraping_files/' + filepath_list[filepath_idx]

        df = pd.read_csv(filepath)

        for _, row in df.iterrows():

            data_df = pd.DataFrame()

            check = True

            for novel_data in novel_datas:

                # 이미 소설이 DB에 있다면, 링크 정보가 DB에 있는지 확인
                # 없는 링크 정보를 포함하고 있다면, DB를 업데이트하기 위해 update list에 추가
                if row['title'] in novel_data:
                    check = False

                    if 'ridi' in filepath and novel_data[12] is None:
                        novel_data[12] = row['novel_link']
                        update_novel_list.append(novel_data)
                        create_alert('{}작품이 리디 플랫폼에 추가되었습니다.'.format(row['title']),
                                     'https://www.novelforum.site/novel/{}'.format(row['novel_idx']),
                                     favorite_author_datas,
                                     row['author_idx'],
                                     insert_alert_list)

                    if 'series' in filepath and novel_data[13] is None:
                        novel_data[13] = row['novel_link']
                        update_novel_list.append(novel_data)
                        create_alert('{}작품이 시리즈 플랫폼에 추가되었습니다.'.format(row['title']),
                                     'https://www.novelforum.site/novel/{}'.format(row['novel_idx']),
                                     favorite_author_datas,
                                     row['author_idx'],
                                     insert_alert_list)

                    if 'kakao' in filepath and novel_data[14] is None:
                        novel_data[14] = row['novel_link']
                        update_novel_list.append(novel_data)
                        create_alert('{}작품이 카카오 플랫폼에 추가되었습니다.'.format(row['title']),
                                     'https://www.novelforum.site/novel/{}'.format(row['novel_idx']),
                                     favorite_author_datas,
                                     row['author_idx'],
                                     insert_alert_list)

                    if 'munpia' in filepath and novel_data[15] is None:
                        novel_data[15] = row['novel_link']
                        update_novel_list.append(novel_data)
                        create_alert('{}작품이 문피아 플랫폼에 추가되었습니다.'.format(row['title']),
                                     'https://www.novelforum.site/novel/{}'.format(row['novel_idx']),
                                     favorite_author_datas,
                                     row['author_idx'],
                                     insert_alert_list)

                    break

            # 기존 DB에 없는 소설이 있다면 DB에 넣게 insert list에 추가
            if check:
                data_df['title'] = row['title']
                data_df['summary'] = row['synopsis']
                data_df['cover_image'] = row['img_link']
                data_df['episode'] = row['total_episode']
                data_df['price'] = row['total_episode']
                data_df['download_cnt'] = row['comment']

                # 작가 찾기
                author_check = True

                for author_data in author_datas:
                    if row['author'] in author_data:
                        data_df['author_idx'] = author_data[1]
                        author_check = False
                        break

                if author_check:
                    insert_author_list.append(row['author'])





                data_df['rating'] = 0
                data_df['review_cnt'] = 0
                data_df['category'] = row['genre']
                data_df['is_finished'] = row['is_complite']

                if 'ridi' in filepath:
                    data_df['is_ridi'] = row['novel_link']
                    data_df['is_naver'] = None
                    data_df['is_kakao'] = None
                    data_df['is_munpia'] = None

                if 'series' in filepath:
                    data_df['is_naver'] = row['novel_link']
                    data_df['is_ridi'] = None
                    data_df['is_kakao'] = None
                    data_df['is_munpia'] = None

                if 'kakao' in filepath:
                    data_df['is_kakao'] = row['novel_link']
                    data_df['is_ridi'] = None
                    data_df['is_naver'] = None
                    data_df['is_munpia'] = None

                if 'munpia' in filepath:
                    data_df['is_munpia'] = row['novel_link']
                    data_df['is_ridi'] = None
                    data_df['is_naver'] = None
                    data_df['is_kakao'] = None

                insert_novel_list.append(data_df.values.tolist())




    print(update_novel_list)
    print('==================================================')
    print(insert_author_list)
















