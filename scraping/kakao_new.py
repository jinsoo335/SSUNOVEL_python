"""
신작 탭의 href를 추출하여 카카오href.csv에 이어붙입니다.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

# 브라우저 꺼짐 방지
chrome_options = Options()
#chrome_options.add_argument("headless")
chrome_options.add_experimental_option("detach", True)
#chrome_options.add_argument("headless")  # 백그라운드에서 작업
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
            data = browser.find_element(By.CSS_SELECTOR,
                                        f'#__next > div > div.flex.w-full.grow.flex-col.px-122pxr > div > div.flex.grow.flex-col > div.mb-4pxr.flex-col > div > div.px-11pxr > div > div > div:nth-child({i}) > div > a').get_attribute(
                'href')
            url_list.append(data)
            i += 1
        except:  # 더 이상 href 파싱이 불가능하면 break;
            break
    info = {"link_list": url_list}
    save_url = pd.DataFrame(info)
    print(save_url.head())
    save_url.set_index('link_list')
    save_url.to_csv(save_name + ".csv", encoding="UTF-8")

    browser.quit()
    return




def kakao_new():
    href_name = 'kakao_new'
    save_href_list(href_name, 'https://page.kakao.com/menu/10011/screen/74?tab_uid=11')

    try:
        href = pd.read_csv(href_name + '.csv', encoding="UTF-8")
    except:
        print("csv 파일을 읽을 수 없습니다.")
        exit(0)

    try :
        old_href = pd.read_csv('kakaohref.csv', encoding="UTF-8")
    except:
        print("csv 파일을 읽을 수 없습니다..")
        exit(0)

    merge_kakao = pd.concat([old_href, href])
    merge_kakao.drop(['Unnamed: 0'], axis = 1, inplace = True)
    merge_kakao.reset_index(drop=True, inplace=True)
    merge_kakao.to_csv('kakaohref.csv', encoding='UTF-8') #새로운 href 파일로 갱신





