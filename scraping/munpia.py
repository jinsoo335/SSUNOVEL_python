import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchAttributeException
from selenium.webdriver.common.by import By
import re
from tqdm.notebook import tqdm
import traceback


def munpia_complete_scraping():

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    #options.add_argument("headless")

    # 창을 미리 열기, 단 백그라운드에서 돌게 하기
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        print("webDriver를 못 생성")

    # 완결 확인
    f = open('./scraping_files/munpia1.csv', 'w', encoding="utf-8-sig", newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(
        ['title', 'is_complete', 'genre', 'author', 'synopsis', 'price', 'total_episode', 'comment', 'img_link',
         'novel_link', 'tags'])

    start_page = 1

    end_page = 123

    # 완결작 메인 페이지 이동
    main_url = "https://novel.munpia.com/page/hd.platinum/group/pl.serial/finish/true/view/allend"

    driver.get(main_url)

    sleep(5)

    index = 1

    try:

        #     # 완결 버튼 누르기
        #     driver.find_element(By.XPATH,'//*[@id="SECTION-MENU"]/ul/li[2]').click()
        #     sleep(1)

        for i in tqdm(range(start_page, end_page + 1)):

            # 웹소설 목록에서 한 페이지씩 옆으로 이동하는 부분
            li_tag = driver.find_element(By.XPATH, '//*[@id="NOVELOUS-CONTENTS"]/section[6]/ul/li[{}]'.format(index))
            li_tag.click()

            index += 1

            if index > 6:
                index = 6

            sleep(2)

            source = driver.page_source
            soup = BeautifulSoup(source, 'lxml')

            a_tags = soup.find_all("a", attrs={"class": "title col-xs-6"})

            if a_tags is None:
                continue

            for a_tag_index in range(len(a_tags)):
                novel_info_url = a_tags[a_tag_index]["href"]
                info_res = requests.get(novel_info_url)
                info_res.raise_for_status()

                sleep(2)

                info_soup = BeautifulSoup(info_res.text, 'lxml')

                try:
                    detail_div = info_soup.find("div", attrs={"class": "dd detail-box"})

                    # 제목
                    title = detail_div.find("h2").find("a")["title"]

                    # 연재 여부
                    # is_complite = info_soup.find("p", attrs={"class": "meta-path"}).find_all("span")[1].get_text()
                    is_complite = "완결"

                    # 장르
                    genre = info_soup.find("p", attrs={"class": "meta-path"}).find("strong").get_text()

                    # 작가명
                    author = info_soup.find("a", attrs={"class": "member-trigger"}).find("strong").get_text()

                    # 개요
                    synopsis = info_soup.find("p", attrs={"class": "story"}).get_text()

                    # 가격
                    price = info_soup.find("span", attrs={"style": "color:#989898"}).text
                    price = price.strip().split()[0]

                    # 총 회차
                    total_episode = detail_div.find_all("dl", attrs={"class": "meta-etc meta"})[1].find("dd").get_text()
                    total_episode = re.sub(r"[^0-9]", "", total_episode)
                    total_episode = int(total_episode)

                    # 표지 이미지 링크
                    img_link = info_soup.find("img", attrs={"class": "cover"})["src"]

                    # 댓글 수
                    comment_start_page = 1
                    comment_end_page = int(total_episode / 30)

                    if total_episode % 30 != 0:
                        comment_end_page += 1

                    comment_cnt = 0

                    for comment_index in range(comment_start_page, comment_end_page + 1):

                        comment_info_url = novel_info_url + "/page/{}".format(comment_index)
                        comment_info_res = requests.get(comment_info_url)
                        comment_info_res.raise_for_status()

                        sleep(1)

                        comment_soup = BeautifulSoup(comment_info_res.text, 'lxml')

                        comments = comment_soup.find_all("a", attrs={"class": "comment trigger-window"})

                        for comment in comments:
                            comment_cur_cnt = comment.get_text()
                            comment_cur_cnt = re.sub(r"[^0-9]", "", comment_cur_cnt)
                            comment_cur_cnt = int(comment_cur_cnt)

                            comment_cnt += comment_cur_cnt

                    # 태그 정보 가져오기
                    tags = ""

                    tag_div = info_soup.find("div", attrs={"class": "tag-list expand"})

                    if tag_div is not None:
                        tags_a = tag_div.find_all("a")

                        for tag_a in tags_a:
                            tags += tag_a.get_text().strip()
                    else:
                        tags += genre

                    tags = re.sub("#", ",", tags)
                    tags = tags.strip(',')


                    datas.append(
                        [title, is_complite, genre, author, synopsis, price, total_episode, comment_cnt, img_link,
                         novel_info_url, tags])

                except Exception:
                    #print('error')
                    #print(traceback.format_exc())
                    continue



    except Exception:
        print("error")
        print(title, i)
        print(traceback.format_exc())

    finally:
        writer.writerows(datas)
        driver.quit()
        f.close


def munpia_incomplete_scraping():

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    #options.add_argument("headless")

    # 창을 미리 열기, 단 백그라운드에서 돌게 하기
    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        print("webDriver를 못 생성")

    # 연재 중 확인
    f = open('./scraping_files/munpia0.csv', 'w', encoding="utf-8-sig", newline='')
    writer = csv.writer(f)
    datas = []
    datas.append(
        ['title', 'is_complete', 'genre', 'author', 'synopsis', 'price', 'total_episode', 'comment', 'img_link',
         'novel_link', 'tags'])

    start_page = 1

    end_page = 18

    # 메인 페이지 이동
    main_url = "https://novel.munpia.com/page/hd.platinum/group/pl.serial/view/serial"

    driver.get(main_url)

    sleep(5)

    index = 1

    try:

        for i in tqdm(range(start_page, end_page + 1)):

            # 웹소설 목록에서 한 페이지씩 옆으로 이동하는 부분
            li_tag = driver.find_element(By.XPATH, "//*[@id='NOVELOUS-CONTENTS']/section[4]/ul/li[{}]".format(index))
            li_tag.click()

            index += 1

            if index > 6:
                index = 6

            sleep(2)

            source = driver.page_source
            soup = BeautifulSoup(source, 'lxml')

            a_tags = soup.find_all("a", attrs={"class": "title col-xs-6"})

            if a_tags is None:
                continue

            for a_tag_index in range(len(a_tags)):
                novel_info_url = a_tags[a_tag_index]["href"]
                info_res = requests.get(novel_info_url)
                info_res.raise_for_status()

                sleep(2)

                info_soup = BeautifulSoup(info_res.text, 'lxml')

                try:
                    detail_div = info_soup.find("div", attrs={"class": "dd detail-box"})

                    # 제목
                    title = detail_div.find("h2").find("a")["title"]

                    # 연재 여부
                    is_complite = info_soup.find("p", attrs={"class": "meta-path"}).find_all("span")[1].get_text()

                    # 장르
                    genre = info_soup.find("p", attrs={"class": "meta-path"}).find("strong").get_text()

                    # 작가명
                    author = info_soup.find("a", attrs={"class": "member-trigger"}).find("strong").get_text()

                    # 개요
                    synopsis = info_soup.find("p", attrs={"class": "story"}).get_text()

                    # 가격
                    price = info_soup.find("span", attrs={"style": "color:#989898"}).text
                    price = price.strip().split()[0]

                    # 총 회차
                    total_episode = detail_div.find_all("dl", attrs={"class": "meta-etc meta"})[1].find("dd").get_text()
                    total_episode = re.sub(r"[^0-9]", "", total_episode)
                    total_episode = int(total_episode)

                    # 표지 이미지 링크
                    img_link = info_soup.find("img", attrs={"class": "cover"})["src"]

                    # 댓글 수
                    comment_start_page = 1
                    comment_end_page = int(total_episode / 30)

                    if total_episode % 30 != 0:
                        comment_end_page += 1

                    comment_cnt = 0

                    for comment_index in range(comment_start_page, comment_end_page + 1):

                        comment_info_url = novel_info_url + "/page/{}".format(comment_index)
                        comment_info_res = requests.get(comment_info_url)
                        comment_info_res.raise_for_status()

                        sleep(1)

                        comment_soup = BeautifulSoup(comment_info_res.text, 'lxml')

                        comments = comment_soup.find_all("a", attrs={"class": "comment trigger-window"})

                        for comment in comments:
                            comment_cur_cnt = comment.get_text()
                            comment_cur_cnt = re.sub(r"[^0-9]", "", comment_cur_cnt)
                            comment_cur_cnt = int(comment_cur_cnt)

                            comment_cnt += comment_cur_cnt

                    tags = ""

                    tag_div = info_soup.find("div", attrs={"class": "tag-list expand"})

                    if tag_div is not None:
                        tags_a = tag_div.find_all("a")

                        for tag_a in tags_a:
                            tags += tag_a.get_text().strip()
                    else:
                        tags += genre

                    tags = re.sub("#", ",", tags)
                    tags = tags.strip(',')

                    datas.append(
                        [title, is_complite, genre, author, synopsis, price, total_episode, comment_cnt, img_link,
                         novel_info_url, tags])

                except Exception:
                    print('error')
                    print(traceback.format_exc())
                    continue



    except Exception:
        print("error")
        print(title, i)
        print(traceback.format_exc())

    finally:
        writer.writerows(datas)
        driver.quit()
        f.close


def munpia_scraping():

    munpia_complete_scraping()

    munpia_incomplete_scraping()
