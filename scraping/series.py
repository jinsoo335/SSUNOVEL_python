import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
from selenium import webdriver
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchAttributeException
from selenium.webdriver.common.by import By
import re
from tqdm.notebook import tqdm
import traceback


# title         :       제목            string 타입         error나거나 비어있으면 ""
# score         :       평점            float 타입          error나거나 비어있으면 -1
# total_episode :       총 회차 수      int 타입            error나거나 비어있으면 -1
# price         :       회당 소장 가격   int 타입           error나거나 비어있으면 -1      무료는 0
# synopsis      :       개요            String 타입        error나거나 비어있으면 ""
# is_complite   :       연재 중 정보    String 타입         error나거나 비어있으면 ""
# genre         :       장르            String 타입         error나거나 비어있으면 ""
# author        :       작가            String 타입         error나거나 비어있으면 ""
# img_link      :       작품 표지 링크  String 타입          error나거나 비어있으면 ""
# comment       :       댓글 수         int 타입            error나거나 비어있으면 -1       , 제거

def series_scraping():

    start_page = 1
    end_page = 3045
    sleep_time = 1

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    #options.add_argument("headless")

    # 창을 미리 열기, 단 백그라운드에서 돌게 하기
    try:
        browser = webdriver.Chrome(options=options)
    except Exception:
        print("webDriver를 못 생성")

    f = open('./scraping_files/naver.csv', 'w', encoding="utf-8-sig", newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(
        ['title', 'is_complete', 'genre', 'author', 'synopsis', 'price', 'total_episode', 'comment', 'img_link',
         'novel_link', 'tags'])

    try:
        for i in tqdm(range(start_page, end_page + 1)):

            try:
                url = "https://series.naver.com/novel/categoryProductList.series?categoryTypeCode=all&genreCode=&orderTypeCode=sale&is&isFinished=false&page={}".format(
                    i)
                res = requests.get(url)

                sleep(sleep_time)

                res.raise_for_status()
                soup = BeautifulSoup(res.text, 'lxml')

                items = soup.find_all("div", attrs="cont cont_v2")
                a_tags = soup.find_all("a", attrs={"class": "pic NPI=a:content"})

            except KeyboardInterrupt:
                raise

            except:
                print(traceback.format_exc())
                continue

            for a_tag_idx in range(len(a_tags)):

                try:

                    # 19금 거르기
                    if items[a_tag_idx].find('em', attrs={"class": "ico n19"}):
                        continue

                    if a_tags[a_tag_idx]["href"]:
                        novel_info_url = "https://series.naver.com{}".format(a_tags[a_tag_idx]["href"])
                        info_res = requests.get(novel_info_url)

                        info_res.raise_for_status()
                        info_soup = BeautifulSoup(info_res.text, "lxml")

                        # 판매 중지된 작품 제외
                        if info_soup.find('body', attrs={"class": "type_error_series_on"}):
                            continue

                        # get
                        # get 하면서 페이지가 로딩될 때까지 잠깐 기다리기
                        browser.get(novel_info_url)
                        sleep(sleep_time)

                        # title
                        # 제목 부분
                        end_head_div = info_soup.find("div", attrs={"class": "end_head"})
                        title = end_head_div.find('h2').get_text()

                        # score
                        # 시리즈 앱 내에서의 평점 정보
                        score_div = end_head_div.find('div', attrs={"class": "score_area"})
                        score = score_div.find('em').get_text()
                        score = float(score)

                        #   total_episode
                        #   총 회차 수 부분
                        h5_end_total_episode = info_soup.find("h5", attrs={"class": "end_total_episode"})
                        total_episode = h5_end_total_episode.find('strong').get_text()
                        total_episode = re.sub(r"[^0-9]", "", total_episode)
                        total_episode = int(total_episode)

                        #   price
                        #   가격 정보 부분
                        #   무료, 1의 2가지 값 중 하나를 가짐을 추정
                        price_div = info_soup.find('div', attrs={"class": "area_price"})
                        price = price_div.find('span', attrs={"class": "point_color"}).get_text()  # 무료, 1 값을 가짐
                        if price == '무료':
                            price = 0
                        else:
                            price = re.sub(r"[^0-9]", "", price)
                            price = int(price)

                        #   synopsis
                        #   소설 개요 부분
                        un_display = info_soup.find("div", attrs={"class": "_synopsis", "style": "display: none"})

                        synopsis = ""
                        if un_display:
                            for content in un_display.contents:
                                if content is None:
                                    continue
                                elif content.name == 'span':
                                    continue
                                elif content.name == 'br':
                                    synopsis += "\n"
                                elif content is not None:
                                    try:
                                        synopsis += content.get_text(strip=True)
                                    except AttributeError:
                                        synopsis += content.strip()
                        else:
                            synopsis += info_soup.find("div", attrs={"class": "_synopsis"}).get_text()

                        #   li
                        #   is_complite, genre, author
                        #   연재중, 장르, 작가 정보
                        li_infos = info_soup.find('li', attrs={"class": "info_lst"})

                        is_complite = ""

                        if li_infos.find('li', attrs={"class": "ing"}):
                            is_complite += '연재중'
                        else:
                            is_complite += '완결'

                        genre_and_author = li_infos.find_all('a')

                        genre = genre_and_author[0].get_text()
                        author = genre_and_author[1].get_text()

                        # img_link
                        # 작품 표지 이미지 링크
                        img_span = info_soup.find('span', attrs={"class": "pic_area"})
                        img_link = ""

                        if img_span:
                            img_link += img_span.find('img')['src']
                        else:
                            img_a = info_soup.find('a', attrs={'class': "pic_area"})
                            img_link += img_a.find('img')['src']

                        # comment
                        # 댓글 수
                        comment = browser.find_element(By.CLASS_NAME, 'u_cbox_count').text
                        comment = re.sub(r"[^0-9]", "", comment)
                        comment = int(comment)

                        # tags
                        tags = ""
                        tags += genre

                        datas.append(
                            [title, is_complite, genre, author, synopsis, price, total_episode, comment, img_link,
                             novel_info_url, tags])

                except KeyboardInterrupt:
                    raise
                except:
                    #print(traceback.format_exc())
                    continue


    except Exception:

        # 제목과 추적용 page 출력
        #print(i)
        #print(title)

        print('에러 뜸')
        #print(traceback.format_exc())
    finally:
        writer.writerows(datas)
        browser.quit()
        f.close()