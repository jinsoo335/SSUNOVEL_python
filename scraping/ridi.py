import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchAttributeException
from selenium.webdriver.common.by import By
import re
from tqdm.notebook import tqdm
import traceback

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("headless") #백그라운드에서 작업
# 드라이버 생성 및 열기
service = Service(executable_path=ChromeDriverManager().install())

def repeat_scroll(driver):
    # 페이지 전체 높이
    page_height = driver.execute_script("return document.body.scrollHeight")

    # 스크롤을 내릴 높이
    distance = page_height / 20

    # 스크롤 시작 위치
    start = 1

    # 스크롤을 내리면서 태그 정보를 가져올 수 있게 하기
    # 1초씩 기다기
    for i in range(20):
        driver.execute_script("window.scrollTo(0, {})".format(start))
        sleep(0.5)
        start += distance


def ridi_fantasy_scraping():

    # 창을 미리 열기, 단 백그라운드에서 돌게 하기
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        print("webDriver를 못 생성")

    f = open('./scraping_files/ridi0.csv', 'w', encoding="utf-8-sig", newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(
        ['title', 'is_complete', 'genre', 'author', 'synopsis', 'price', 'total_episode', 'comment', 'img_link',
         'novel_link', 'tags'])

    # 시작 페이지
    start_page = 1

    # 마지막 페이지
    end_page = 147

    try:

        for i in tqdm(range(start_page, end_page + 1)):
            url = "https://ridibooks.com/category/books/1750?page={}&adult_exclude=y".format(i)

            # 셀레니움 이용해서 스크롤 밑으로 내리기
            driver.get(url)
            repeat_scroll(driver)

            # 페이지 소스 파싱
            source = driver.page_source
            soup = BeautifulSoup(source, 'lxml')

            # li_tags = soup.find_all("li", attrs={"class" : "fig-ko232"})
            a_tags = soup.find_all("a", attrs={"class": "fig-1rb85bg"})

            if a_tags is None:
                continue

            for a_tag_idx in range(len(a_tags)):
                novel_info_url = "https://ridibooks.com" + a_tags[a_tag_idx]["href"]
                info_res = requests.get(novel_info_url)
                info_res.raise_for_status()

                sleep(2)

                info_soup = BeautifulSoup(info_res.text, 'lxml')

                # title   제목 가져오기
                try:
                    title = info_soup.find('h1', attrs={"class": "info_title_wrap"}).get_text()
                except Exception:
                    continue

                # is_complite   완결 여부 가져오기
                is_complite = ''

                if info_soup.find('span', attrs={'class': 'metadata_item complete'}):
                    is_complite = '완결'
                elif info_soup.find('span', attrs={'class': "metadata_item not_complete"}):
                    is_complite = '미완결'

                # genre 장르 가져오기
                genre = info_soup.find("p", attrs={"class": "info_category_wrap"})

                try:
                    genre = genre.find_all("a")[1].get_text()
                except Exception:
                    continue

                # author   작가 가져오기
                try:
                    author = info_soup.find("a", attrs={"class": "js_author_detail_link author_detail_link"}).get_text()
                except Exception:
                    continue

                # price   가격 가져오기  price는 소설 목록 페이지에서 가져와야 한다.
                try:
                    price = soup.find("span", attrs={"class": "fig-162akm6"}).get_text()
                except Exception:
                    continue

                # synopsis   줄거리 가져오기
                try:
                    synopsis = info_soup.find("p", attrs={"class": "introduce_paragraph"}).get_text()
                except Exception:
                    continue

                # total_episode   총 회차 가져오기

                total_episode = info_soup.find("span", attrs={"class": "metadata_item book_count"})

                if total_episode is None:
                    continue

                total_episode = total_episode.get_text()
                total_episode = re.sub(r"[^0-9]", "", total_episode)
                total_episode = int(total_episode)

                # comment    댓글 수 가져오기
                comment_li_tag = info_soup.find("li", attrs={"class": "tab_list"})
                span_tag = comment_li_tag.find("span", attrs={"class": "num"})
                comment = 0

                if span_tag is not None:
                    comment = int(span_tag.get_text())

                # comment = driver.find_element(By.CLASS_NAME, 'num').text

                # img_link   이미지 링크가져오기
                img_link = info_soup.find("img", attrs={"class": "thumbnail"})["src"]

                # tag 테그 정보 가져오기
                try:
                    tags = ""

                    tag_list = info_soup.find("ul", attrs={"class": "keyword_list"})
                    tag_spans = info_soup.find_all("span", attrs={"class": "keyword"})

                    for tag_span in tag_spans:
                        tags += tag_span.get_text().strip()

                    tags = re.sub("#", ",", tags)
                    tags = tags.strip(",")


                except:
                    print(traceback.format_exc())
                    continue


                datas.append([title, is_complite, genre, author, synopsis, price, total_episode, comment, img_link,
                              novel_info_url, tags])

    except Exception:

        print('error: ', title, i)
        print(traceback.format_exc())

    finally:
        writer.writerows(datas)
        driver.quit()
        f.close()


def ridi_rofan_scraping():

    # 옵션 생성
    #options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    #options.add_argument("headless")

    # 창을 미리 열기, 단 백그라운드에서 돌게 하기
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        print("webDriver를 못 생성")

    # 로멘스 판타지
    f = open('./scraping_files/ridi1.csv', 'w', encoding="utf-8-sig", newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(
        ['title', 'is_complete', 'genre', 'author', 'synopsis', 'price', 'total_episode', 'comment', 'img_link',
         'novel_link', 'tags'])

    # 시작 페이지
    start_page = 1

    # 마지막 페이지
    end_page = 8

    try:

        for i in tqdm(range(start_page, end_page + 1)):
            # 로판 경로 위치
            url = "https://ridibooks.com/category/books/6050?adult_exclude=y&page={}".format(i)

            # 셀레니움 이용해서 스크롤 밑으로 내리기
            driver.get(url)
            repeat_scroll(driver)

            # 페이지 소스 파싱
            source = driver.page_source
            soup = BeautifulSoup(source, 'lxml')

            # li_tags = soup.find_all("li", attrs={"class" : "fig-ko232"})
            a_tags = soup.find_all("a", attrs={"class": "fig-1rb85bg"})

            if a_tags is None:
                continue

            for a_tag_idx in range(len(a_tags)):
                novel_info_url = "https://ridibooks.com" + a_tags[a_tag_idx]["href"]
                info_res = requests.get(novel_info_url)
                info_res.raise_for_status()

                sleep(2)

                info_soup = BeautifulSoup(info_res.text, 'lxml')

                # title   제목 가져오기
                try:
                    title = info_soup.find('h1', attrs={"class": "info_title_wrap"}).get_text()
                except Exception:
                    continue

                # is_complite   완결 여부 가져오기
                is_complite = ''

                if info_soup.find('span', attrs={'class': 'metadata_item complete'}):
                    is_complite = '완결'
                elif info_soup.find('span', attrs={'class': "metadata_item not_complete"}):
                    is_complite = '미완결'

                # genre 장르 가져오기
                genre = info_soup.find("p", attrs={"class": "info_category_wrap"})

                try:
                    genre = genre.find_all("a")[1].get_text()
                except Exception:
                    continue

                # author   작가 가져오기
                try:
                    author = info_soup.find("a", attrs={"class": "js_author_detail_link author_detail_link"}).get_text()
                except Exception:
                    continue

                # price   가격 가져오기  price는 소설 목록 페이지에서 가져와야 한다.
                try:
                    price = soup.find("span", attrs={"class": "fig-162akm6"}).get_text()
                except Exception:
                    continue

                # synopsis   줄거리 가져오기
                try:
                    synopsis = info_soup.find("p", attrs={"class": "introduce_paragraph"}).get_text()
                except Exception:
                    continue

                # total_episode   총 회차 가져오기

                total_episode = info_soup.find("span", attrs={"class": "metadata_item book_count"})

                if total_episode is None:
                    continue

                total_episode = total_episode.get_text()
                total_episode = re.sub(r"[^0-9]", "", total_episode)
                total_episode = int(total_episode)

                # comment    댓글 수 가져오기
                comment_li_tag = info_soup.find("li", attrs={"class": "tab_list"})
                span_tag = comment_li_tag.find("span", attrs={"class": "num"})
                comment = 0

                if span_tag is not None:
                    comment = int(span_tag.get_text())

                # comment = driver.find_element(By.CLASS_NAME, 'num').text

                # img_link   이미지 링크가져오기
                img_link = info_soup.find("img", attrs={"class": "thumbnail"})["src"]

                # tag 테그 정보 가져오기
                try:
                    tags = ""

                    tag_list = info_soup.find("ul", attrs={"class": "keyword_list"})
                    tag_spans = info_soup.find_all("span", attrs={"class": "keyword"})

                    for tag_span in tag_spans:
                        tags += tag_span.get_text()

                    tags = re.sub("#", ",", tags)
                    tags = tags.strip(",")


                except:
                    print(traceback.format_exc())
                    continue


                datas.append([title, is_complite, genre, author, synopsis, price, total_episode, comment, img_link,
                              novel_info_url, tags])

    except Exception:

        print('error: ', title, i)
        print(traceback.format_exc())

    finally:
        writer.writerows(datas)
        driver.quit()
        f.close()


def ridi_romance_scraping():

    # 옵션 생성
    #options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    #options.add_argument("headless")

    # 창을 미리 열기, 단 백그라운드에서 돌게 하기
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        print("webDriver를 못 생성")

    # 로멘스
    f = open('./scraping_files/ridi2.csv', 'w', encoding="utf-8-sig", newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(
        ['title', 'is_complete', 'genre', 'author', 'synopsis', 'price', 'total_episode', 'comment', 'img_link',
         'novel_link', 'tags'])

    # 시작 페이지
    start_page = 1

    # 마지막 페이지
    end_page = 7

    try:

        for i in tqdm(range(start_page, end_page + 1)):
            # 로멘스 경로 위치
            url = "https://ridibooks.com/category/books/1650?adult_exclude=y&page={}".format(i)

            # 셀레니움 이용해서 스크롤 밑으로 내리기
            driver.get(url)
            repeat_scroll(driver)

            # 페이지 소스 파싱
            source = driver.page_source
            soup = BeautifulSoup(source, 'lxml')

            # li_tags = soup.find_all("li", attrs={"class" : "fig-ko232"})
            a_tags = soup.find_all("a", attrs={"class": "fig-1rb85bg"})

            if a_tags is None:
                continue

            for a_tag_idx in range(len(a_tags)):
                novel_info_url = "https://ridibooks.com" + a_tags[a_tag_idx]["href"]
                info_res = requests.get(novel_info_url)
                info_res.raise_for_status()

                sleep(2)

                info_soup = BeautifulSoup(info_res.text, 'lxml')

                # title   제목 가져오기
                try:
                    title = info_soup.find('h1', attrs={"class": "info_title_wrap"}).get_text()
                except Exception:
                    continue

                # is_complite   완결 여부 가져오기
                is_complite = ''

                if info_soup.find('span', attrs={'class': 'metadata_item complete'}):
                    is_complite = '완결'
                elif info_soup.find('span', attrs={'class': "metadata_item not_complete"}):
                    is_complite = '미완결'

                # genre 장르 가져오기
                genre = info_soup.find("p", attrs={"class": "info_category_wrap"})

                try:
                    genre = genre.find_all("a")[1].get_text()
                except Exception:
                    continue

                # author   작가 가져오기
                try:
                    author = info_soup.find("a", attrs={"class": "js_author_detail_link author_detail_link"}).get_text()
                except Exception:
                    continue

                # price   가격 가져오기  price는 소설 목록 페이지에서 가져와야 한다.
                try:
                    price = soup.find("span", attrs={"class": "fig-162akm6"}).get_text()
                except Exception:
                    continue

                # synopsis   줄거리 가져오기
                try:
                    synopsis = info_soup.find("p", attrs={"class": "introduce_paragraph"}).get_text()
                except Exception:
                    continue

                # total_episode   총 회차 가져오기
                total_episode = info_soup.find("span", attrs={"class": "metadata_item book_count"})

                if total_episode is None:
                    continue

                total_episode = total_episode.get_text()
                total_episode = re.sub(r"[^0-9]", "", total_episode)
                total_episode = int(total_episode)

                # comment    댓글 수 가져오기
                comment_li_tag = info_soup.find("li", attrs={"class": "tab_list"})
                span_tag = comment_li_tag.find("span", attrs={"class": "num"})
                comment = 0

                if span_tag is not None:
                    comment = int(span_tag.get_text())

                # comment = driver.find_element(By.CLASS_NAME, 'num').text

                # img_link   이미지 링크가져오기
                img_link = info_soup.find("img", attrs={"class": "thumbnail"})["src"]

                # tag 테그 정보 가져오기
                try:
                    tags = ""

                    tag_list = info_soup.find("ul", attrs={"class": "keyword_list"})
                    tag_spans = info_soup.find_all("span", attrs={"class": "keyword"})

                    for tag_span in tag_spans:
                        tags += tag_span.get_text()

                    tags = re.sub("#", ",", tags)
                    tags = tags.strip(",")


                except:
                    #print(traceback.format_exc())
                    continue


                datas.append([title, is_complite, genre, author, synopsis, price, total_episode, comment, img_link,
                              novel_info_url, tags])

    except Exception:

        print('error: ', title, i)
        #print(traceback.format_exc())

    finally:
        writer.writerows(datas)
        driver.quit()
        f.close()


def ridi_scraping():

    ridi_fantasy_scraping()

    ridi_romance_scraping()

    ridi_rofan_scraping()
