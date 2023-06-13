"""
기존에 있는 href 을 이용하여 파싱을 진행하는 python 파일입니다.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
import pandas as pd
import time

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("headless") #백그라운드에서 작업
# 드라이버 생성 및 열기
service = Service(executable_path=ChromeDriverManager().install())


# start_url 에 해당하는 모든 웹 소설의 [href]의 값을 csv형태로 저장한다
def save_href_list(save_name, start_url):
    # 드라이버 생성 및 열기
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get(start_url)

    ## 카카오페이지는 무한 스크롤로 구현되어 있어, 스크롤을 맨 밑까지 내린 후 크롤링을 한다.
    before_h = browser.execute_script("return window.scrollY")

    try:
        while True:
            # 맨 아래로 스크롤을 내린다.
            browser.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.END)

            # 스크롤 사이 페이지 로딩 시간
            time.sleep(2)

            # 스크롤 후 높이
            after_h = browser.execute_script("return window.scrollY")

            # 스크롤 끝까지 내려왔다면 스크롤 내리기 취소
            if (after_h == before_h):
                break
            before_h = after_h
    except Exception as ex:
        print(ex)


    i = 1
    url_list = []
    while (True):
        try:
            data = browser.find_element(By.CSS_SELECTOR, f'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div > div > div > div.flex.grow.flex-col > div > div > div > div:nth-child({i}) > div > a').get_attribute('href')
            #data = browser.find_element(By.CSS_SELECTOR,
            #                            f'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.mb-4pxr.flex-col > div > div.px-11pxr > div > div > div:nth-child({i}) > div > a').get_attribute(
            #    'href')
            # __next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div > div > div > div.flex.grow.flex-col > div > div > div > div:nth-child(1) > div
            url_list.append(data)
            i += 1
        except:  # 더 이상 href 파싱이 불가능하면 break;
            break
    info = {"url_list": url_list}
    save_url = pd.DataFrame(info)
    save_url.set_index('url_list')
    save_url.to_csv(save_name + ".csv", encoding="UTF-8")
    browser.quit()
    return


# save_name : 저장할 이름
def save_kakako_novel_info(save_name, url_list, idx):
    # 크롤링 한 데이터들을 append
    title_list = []
    image_url_list = []
    author_list = []
    genre_list = []
    total_episode_list = []
    comment_cnt_list = []
    complete_list = []
    synoposis_list = []
    price_list = []
    link_list = []
    themes_list = []

    browser = webdriver.Chrome(service=service, options=chrome_options)

    # 1000 개씩 나눠서 작업
    print(f"{idx} : 이번 작업의 url list 길이는 {len(url_list)} 입니다")
    for i in tqdm(range(len(url_list))):
        url = url_list[i]
        browser.get(url)
        browser.implicitly_wait(2)  # URL이 모두 로딩 될 때까지 대기
        try:
            title = browser.find_element(By.CSS_SELECTOR, "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                                          "div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > "
                                                          "div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > "
                                                          "div.relative.text-center.mx-32pxr.py-24pxr > span").text

            image_url = browser.find_element(By.CSS_SELECTOR,
                                             "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                             "div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > "
                                             "div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > "
                                             "div.mx-auto.css-1cyn2un-ContentOverviewThumbnail > div > div > "
                                             "img").get_attribute('src')

            author = browser.find_element(By.CSS_SELECTOR, "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                                           "div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > "
                                                           "div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > "
                                                           "div.relative.text-center.mx-32pxr.py-24pxr > div:nth-child(2) > "
                                                           "div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el-50"
                                                           ".opacity-100.all-child\:font-small2 > div.mt-4pxr > span").text

            time.sleep(0.5)

            total_episode = browser.find_element(By.CSS_SELECTOR,
                                                 "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                                 "div.flex.h-full.flex-1 > "
                                                 "div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div:nth-child(2) "
                                                 "> div:nth-child(1) > "
                                                 "div.flex.h-44pxr.w-full.flex-row.items-center.justify-between"
                                                 ".px-15pxr.bg-bg-a-20 > "
                                                 "div.flex.h-full.flex-1.items-center.space-x-8pxr > span").text

            total_episode_split = total_episode.split()
            total_episode = total_episode_split[1]

            comment_cnt = browser.find_element(By.CSS_SELECTOR,
                                               "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                               "div.flex.h-full.flex-1 > "
                                               "div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div:nth-child(2) > "
                                               "div.mt-4pxr.bg-bg-a-20 > div > div > "
                                               "div.relative.flex.w-full.flex-col.bg-transparent.mt-16pxr.mb"
                                               "-24pxr.px-15pxr > span").text

            comment_cnt_split = comment_cnt.split()
            comment_cnt = comment_cnt_split[1].replace('(', '').replace(')', '')

            complete = browser.find_element(By.CSS_SELECTOR,
                                            "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                            "div.flex.h-full.flex-1 > div.mb-28pxr.flex.w-320pxr.flex-col > "
                                            "div:nth-child(1) > div.w-320pxr.css-0 > div > div.css-0 > "
                                            "div.relative.text-center.mx-32pxr.py-24pxr > div:nth-child(2) > "
                                            "div.flex.items-center.justify-center.mt-4pxr.flex-col.text-el"
                                            "-50.opacity-100.all-child\:font-small2 > div:nth-child(1) > "
                                            "span").text

            # 연재 중이면
            if ("완결" != complete):
                complete = "연재중"

            browser.get(url + "?tab_type=about")
            browser.implicitly_wait(2)  # URL이 모두 로딩 될 때까지 대기

            synopsis = browser.find_element(By.CSS_SELECTOR,
                                            "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                            "div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col "
                                            "> div.flex-1.bg-bg-a-20 > div.text-el-60.break-keep.py-20pxr.pt-31pxr.pb-32pxr > span").text
            price = browser.find_element(By.CSS_SELECTOR, "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > "
                                                          "div.flex.h-full.flex-1 > div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col >"
                                                          " div.flex-1.bg-bg-a-20 > div.flex.pr-32pxr > div:nth-child(1) > "
                                                          "div.mt-16pxr.px-32pxr > div:nth-child(4) > div").text
            split_price = price.split('/')
            split_second_split = split_price[0].split('원')
            price = split_second_split[0]

            genre = browser.find_element(By.CSS_SELECTOR,
                                         "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 > "
                                         "div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col > div.flex-1.bg-bg-a-20 > div.flex.pr-32pxr "
                                         "> div:nth-child(1) > div.mt-16pxr.px-32pxr > div:nth-child(1) > div > span:nth-child(3)").text
            j = 1
            theme = ""
            while True:
                try:
                    tag = browser.find_element(By.CSS_SELECTOR,
                                               "#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div.flex.h-full.flex-1 "
                                               "> div.mb-28pxr.ml-4px.flex.w-632pxr.flex-col "
                                               "> div.flex-1.bg-bg-a-20 > div:nth-child(1) > "
                                               f"div.flex.flex-wrap.px-32pxr > a:nth-child({j}) > button").text
                    theme += tag[1:]
                    theme += ","
                    j += 1
                except Exception as ex:
                    if theme == "":
                        theme += genre
                    else :
                        theme = theme[0:len(theme) - 1]
                    break

            # 크롤링이 끝나면 추가
            title_list.append(title)
            complete_list.append(complete)
            genre_list.append(genre)
            author_list.append(author)
            synoposis_list.append(synopsis)
            price_list.append(price)
            comment_cnt_list.append(comment_cnt)
            image_url_list.append(image_url)
            total_episode_list.append(total_episode)
            link_list.append(url)
            themes_list.append(theme)

            # 한 소설 작업이 끝나면 1초 휴식
            time.sleep(0.5)

        except:
            continue

    # 가진 정보를 판다스로 변환후 CSV 파일로 저장
    info = {"title": title_list, "is_complete": complete_list, "genre": genre_list, "author": author_list,
            "synopsis": synoposis_list, "price": price_list, "total_episode": total_episode_list,
            "comment": comment_cnt_list, "img_link": image_url_list, "novel_link": link_list, "tags" : themes_list}

    novel = pd.DataFrame(info)
    result = novel.set_index("title")  # remove index

    result.to_csv(f"{save_name}.csv", encoding="UTF-8")
    browser.quit()

    return


def kakao_present():
    href_name = 'kakaohref.csv' #파싱할 href가 담겨있는 link.

    try:
        href = pd.read_csv(href_name, encoding="UTF-8")
    except:
        print("csv 파일을 읽을 수 없습니다.")
        exit(0)

    h = href['link_list']
    url_list = h.to_list()

    length = int(len(url_list)/1000)+1

    result = pd.DataFrame()

    l = []

    #1000개당 csv 파일 하나 생성
    for i in range(length):
        save_kakako_novel_info('kakao_'+str(i), url_list[i * 1000:(i * 1000) + 1000], i)

    # 파싱한 소설 정보 .csv 파일을 모두 이어 붙임
    for i in range(length) :
        try :
            sub = pd.read_csv('kakao_'+str(i)+".csv", encoding='UTF-8')
            l.append(sub)
        except:
            print(f'{i} cant merge sub!!')
            exit(0)

    #인덱스 제거
    result = pd.concat(l)
    result.set_index(keys = 'title', inplace=True)
    result.to_csv('kakao.csv', encoding='UTF-8') #최종 결과를 kakao.csv 파일에 저장
    print("success!!!")






