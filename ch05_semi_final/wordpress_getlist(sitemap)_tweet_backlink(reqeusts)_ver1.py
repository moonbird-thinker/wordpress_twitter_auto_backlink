# -*- coding: utf-8 -*-

import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import platform
import datetime
from tqdm import tqdm
import requests
import re
import pandas as pd
import ssl
from selenium import webdriver
import subprocess
from selenium.webdriver.chrome.service import Service as ChromeService
from pathlib import Path
import os
from time import gmtime
from time import sleep
from time import strftime
from webdriver_manager.chrome import ChromeDriverManager

osName = platform.system()  # window 인지 mac 인지 알아내기 위한

C_END = "\033[0m"
C_BOLD = "\033[1m"
C_INVERSE = "\033[7m"
C_BLACK = "\033[30m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_PURPLE = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"
C_BGBLACK = "\033[40m"
C_BGRED = "\033[41m"
C_BGGREEN = "\033[42m"
C_BGYELLOW = "\033[43m"
C_BGBLUE = "\033[44m"
C_BGPURPLE = "\033[45m"
C_BGCYAN = "\033[46m"
C_BGWHITE = "\033[47m"

# ======================================================================================================== #
# 해당 환경은 chrome 디버그 모드 환경에서 구동이 됩니다. (크롬 디버그 자료: https://blog.naver.com/moonbird_thinker/221981266201)
# 이 환경에서는 미리 필요한 로그인을 모두 하였을때는 더 편한 수행이 가능합니다. 따라서 아래와 같은 명령어는 윈도우 powershell 에서 한번 수행 후 실행을 시켜주면 더 좋습니다.
# & 'C:\Program Files\Google\Chrome\Application\chrome.exe' --remote-debugging-port=9245 --user-data-dir="C:\chrometemtp13
# 크롬 실행파일의 위치와 포트 번호는 본인의 환경에 맞게 수정하셔야 합니다.
# ======================================================================================================== #

# TODO: wordpress API를 이용한 최근 리스트 받아와서 붙이는 방법(앞선 sitemap 리스트 + 최근 리스트는 wordpress API를 사용하여 업데이트) 추가
# TODO: 여러개의 링크를 백링크로 업로드 가능하도록 변경
# TODO: 여러 워드프레스 sitemap 에 대한 그리고 rss 에 대한 사이트 리스트 업데이트 가능하도록 수정
# TODO: https://kmong.com/@달새2 | https://kmong.com/gig/516365 를 통해...

# [사용자 입력 정보]
# ======================================================================================================== START

# [WORDPRESS] wordpress 업로드 대상이 되는 워드프레스 블로그 주소(본인들의 주소를 적어주시면 됩니다.)와 기본 정보
WP_URL = ''  # 자신의 워드프레스 주소 (ex. https://xxx.mycafe24.com)

# [WORDPRESS] wordpress post 리스트들을 csv 에 저장하기 위한 위치 및 파일명
csv_save_path = "post_urls.csv"

# time 정보
PAUSE_TIME = 1  # 셀레니움 수행도중 중간중간 wait time
LOADING_WAIT_TIME = 3  # 페이지의 로딩 시간
LOGIN_WAIT_TIME = 180  # 로그인시 기다리는 시간
TWEET_WRITE_WAIT_TIME = 300  # 트위터의 경우 너무 짧은 주기로 발행을 하면 계정이 잠기는 현상이 있음 5분 정도가 적당, random.randint(20, 60)

fixed_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Whale/3.19.166.16 Safari/537.36'

# [사용자 입력 정보]
# ======================================================================================================== END


def init_driver():
    # try :
    #     shutil.rmtree(r"C:\chrometemp")  #쿠키 / 캐쉬파일 삭제(캐쉬파일 삭제시 로그인 정보 사라짐)
    # except FileNotFoundError :
    #     pass

    if osName not in "Windows":
        try:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9224 --user-data-dir="~/Desktop/crawling/chromeTemp24"'],
                shell=True, stdout=subprocess.PIPE)  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9224 --user-data-dir="~/Desktop/crawling/chromeTemp24"'],
                shell=True, stdout=subprocess.PIPE)
    else:
        try:
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9224 '
                             r'--user-data-dir="C:\chromeTemp24"')  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen(
                r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9224 '
                r'--user-data-dir="C:\chromeTemp24"')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9224")

    service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\120.0.6099.71\\chromedriver.exe')
    # service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(LOADING_WAIT_TIME)
    return driver


def twitter_login(driver):
    try:
        driver.get('https://twitter.com/home')
        sleep(LOADING_WAIT_TIME)
        driver.find_element(By.CLASS_NAME, 'public-DraftStyleDefault-block.public-DraftStyleDefault-ltr')
        print(f'\n이미 로그인 되어있습니다.')
    except:
        driver.get('https://twitter.com/i/flow/login')
        sleep(LOADING_WAIT_TIME)

        try:
            # print(f'\n{C_BOLD}{C_RED}{C_BGBLACK}[주의: 3분안에 로그인을 완료해주세요!!!]{C_END}')
            pbar = tqdm(total=LOGIN_WAIT_TIME)
            for x in range(LOGIN_WAIT_TIME):
                sleep(1)
                try:
                    driver.find_element(By.CLASS_NAME, 'public-DraftStyleDefault-block.public-DraftStyleDefault-ltr')
                    break
                except:
                    pass
                pbar.update(1)
            pbar.close()
        except:
            print('3분안에 로그인 하지 못했습니다.\n')
            exit()


def get_cookies_session(driver, url):
    driver.get(url)
    sleep(LOADING_WAIT_TIME)

    _cookies = driver.get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
        # print(f"{cookie['name']} = {cookie['value']}")

    _session = requests.Session()
    headers = {
        'User-Agent': fixed_user_agent,
    }
    # print(f'\n{_session.headers}')
    # print(f'\n{_session.cookies}')

    _session.headers.update(headers)  # User-Agent 변경
    # print(f'\n{_session.headers}')

    _session.cookies.update(cookie_dict)  # 응답받은 cookies로  변경
    # print(f'\n{_session.cookies}')

    _cookies = driver.get_cookies()
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
        print(f"{cookie['name']} = {cookie['value']}")

    # 셀레니움 웹 드라이버를 종료(drivet.quit())
    print('\n세션 정보를 얻어왔습니다. 셀레니움 웹 드리이버를 종료하겠습니다.')
    driver.close()
    driver.quit()

    return _session


def get_wordpress_post_lists():
    pre_df = pd.DataFrame(None)

    if not os.path.exists(csv_save_path):
        Path(csv_save_path).touch(exist_ok=True)
    else:
        pre_df = pd.read_csv(csv_save_path)

    """ sitemap 을 이용한 빠른 리스트 업데이트 """
    # 참고자료: https://www.nadeem.tech/automate-your-seo-indexing-strategy-with-python-and-wordpress/
    submit_urls = []
    # TODO: Rank Math sitemap_index.xml(post-sitemap1.xml, post-sitemap2.xml,...)
    # TODO: 워드프레스 자체 제공, wp-sitemap.xml, 웹호스팅 서버에 SimpleXML PHP 익스텐션이 설치되어 있어야 하고 info.php 파일을 루트 폴더에 올려야 합니다. 이미지, 비디오, 뉴스 사이트맵 기능이 없습니다.
    # TODO: Jetpack sitemap.xml(sitemap-1.xml, sitemap-2.xml,...), news-sitemap.xml
    # TODO: All in One SEO
    # TODO: Yoast SEO, sitemap_index.xml

    # Jetpack sitemap 플러그인이 설치된 환경에서만 구동 가능
    post_count = 0
    for idx in range(100):  # sitemap-1,... 당 2000개 max로 저장되어 100x2000=200000 까지 저장할수 있음, 100이라는 숫자는 조절가능
        # print("test1")
        wordpress_sitemap_address = f"{WP_URL}/sitemap-{idx + 1}.xml"
        # print(wordpress_sitemap_address)

        res = requests.get(wordpress_sitemap_address)
        if res.status_code != 200:
            break
        # pattern = '(?<=<loc>)[a-zA-z]+://[^\s]*(?=</loc>)'
        pattern = '<loc>(.*?)</loc>'
        url_info_lists = re.findall(pattern, res.text)

        print
        for url_info in url_info_lists:
            temp_dict = {}
            post_count = post_count + 1
            temp_dict['postUrl'] = f'{url_info}'
            temp_dict['tweet'] = 'X'
            # print(f'{post_count}. {url_info}')
            submit_urls.insert(0,
                               temp_dict)  # 앞쪽에 계속 추가 왜냐면 sitemap 순서가 최근순서가 아님 맨아래가 최신 포스팅, insert는 삽입 위치까지 넣어주어야함 맨앞에
            # submit_urls.append(f'{url_info}')

    print(f'\nwordpress sitemap 정보를 이용하여 ({len(submit_urls)})개의 포스팅 url을 가져오는데 성공하였습니다.')

    columns = ['postUrl', 'tweet']
    df1 = pd.DataFrame(submit_urls, columns=columns)

    print(f'\ndf1 = >')
    print(df1.head(5))
    print(df1.tail(5))

    # total = pre_df._append(df1)
    total = pd.concat([pre_df, df1])  # pre_df 에 하단으로 df1을 붙여준다.

    print(f'\total(pre_df + df1) = >')
    print(total.head(5))
    print(total.tail(5))

    # print(tabulate(df, headers='keys', tablefmt='grid'))
    print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}(total dataFrame)에서 중복된 행을 제거 시작{C_END}')
    total = total.drop_duplicates(subset=['postUrl'], keep="first")
    print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}(total dataFrame)에서 중복된 행을 제거 완료{C_END}')

    print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에 데이터 저장 시작{C_END}')
    total.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
    print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}({csv_save_path})에 데이터 저장 완료{C_END}')

    print(f'\nsitemap을 사용하여 포스팅 리스트를 가져와 ({csv_save_path})로 ({len(total)})개 이하의 포스팅 url을 저장하는데 성공하였습니다.')

    # TODO: wordpress API를 이용한 최근 리스트 받아와서 붙이는 방법(앞선 sitemap 리스트 + 최근 리스트는 wordpress API를 사용하여 업데이트)
    # TODO: https://kmong.com/@달새2 | https://kmong.com/gig/516365 를 통해...


def twitter_backlink_post(_driver):
    print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[트위터 로그인 수동 과정 시작(주의 : 3분 이내에 로그인 과정을 끝내야 합니다.)]', C_END)
    twitter_login(_driver)
    sleep(PAUSE_TIME)
    print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[트위터 로그인 수동 과정 완료]', C_END)

    print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[트위터 로그인 후 쿠키값 저장 및 세션 리턴 시작]', C_END)
    twitter_session = get_cookies_session(_driver, 'https://twitter.com/home')
    sleep(PAUSE_TIME)
    print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[트위터 로그인 후 쿠키값 저장 및 세션 리턴 완료]', C_END)

    # 트위터에 requests 글 작성시에 필요한 queryid 와 token (해당 정보는 크롬 도구(F12) 창의 Network에서 트윗을 작성하였을때 나오는 "CreateTweet" 에서 정보를 얻을 수 있음)
    query_id = "q88fRuxEq8t_M95MIQ53vw"
    bearer_token = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

    now = datetime.datetime.now()
    title_data = now.strftime('%Y년 %m월 %d일')

    df = pd.read_csv(csv_save_path, sep=',')
    if len(df) == 0:
        print(f'\n트윗할 url 존재하지 않습니다. ({csv_save_path})에 트윗할 url 항목이 존재해야 합니다.')
        return

    # print(data['postUrl'][0])
    # print(data['tweet'][0])

    message = ''
    message_check_count = 1
    for idx in range(len(df)):
        if df["tweet"].values[idx] == 'O':
            print(f'{idx + 1}. [SKIP] 해당 ({df["postUrl"].values[idx]})은 이미 백링크가 완료된 리스트입니다. 다음으로 넘어가겠습니다.')
            continue

        # 하나의 링크를 백링크로 업로드
        message = f'{df["postUrl"].values[idx]}'
        print(f'\n{idx + 1}. {message}')

        # TODO: 여러개의 링크를 백링크로 업로드 가능하도록 변경
        # TODO: https://kmong.com/@달새2 | https://kmong.com/gig/516365 를 통해...

        url = f'https://twitter.com/i/api/graphql/{query_id}/CreateTweet'
        params = {
            "variables": {
                "tweet_text": message,
                "dark_request": False,
                'media': {
                    'media_entities': [],
                    'possibly_sensitive': False,
                },
                'semantic_annotation_ids': [],
            },
            'features': {
                'tweetypie_unmention_optimization_enabled': True,
                'responsive_web_edit_tweet_api_enabled': True,
                'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
                'view_counts_everywhere_api_enabled': True,
                'longform_notetweets_consumption_enabled': True,
                'responsive_web_twitter_article_tweet_consumption_enabled': False,
                'tweet_awards_web_tipping_enabled': False,
                'longform_notetweets_rich_text_read_enabled': True,
                'longform_notetweets_inline_media_enabled': True,
                'responsive_web_graphql_exclude_directive_enabled': True,
                'verified_phone_label_enabled': False,
                'freedom_of_speech_not_reach_fetch_enabled': True,
                'standardized_nudges_misinfo': True,
                'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
                'responsive_web_media_download_video_enabled': False,
                'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
                'responsive_web_graphql_timeline_navigation_enabled': True,
                'responsive_web_enhance_cards_enabled': False,
            },
            'fieldToggles': {
                'withArticleRichContentState': False,
            },
            "queryId": query_id
        }

        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': bearer_token,
            'content-type': 'application/json',
            # 'cookie': '_ga=GA1.2.104180137.1686933068; kdt=ACoXaAj8Zx4czgU0SXn7mgsJ0uxJaQY3JgpNh5KC; g_state={"i_l":0}; lang=en; _gid=GA1.2.1793506001.1688861827; dnt=1; guest_id=v1%3A168891094724921519; guest_id_marketing=v1%3A168891094724921519; guest_id_ads=v1%3A168891094724921519; gt=1678040252852891648; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCIPn7zqJAToMY3NyZl9p%250AZCIlN2QwMTQ3OTdlMGYxZTk2MDgzZGUwNmRmOWMzNTM4NzI6B2lkIiVjZmVk%250AZDgxZTE3ZTQ3MDY4ZDUzN2ExNWE4NmIwMjM5Nw%253D%253D--7dab1e2f27b145acd4f47ab096d61edeae466861; auth_token=10d1384190485edcd8d94d60a2378592dafb23d0; ct0=3228b3c71fc8937414dcce0ba86d8e62b2b5ee27023e38c4b0947a1f0dd72aed19f347aa1581371df0d87f591981d6cf987514768a74e542dd5ef2edef49ab901c6e0a186b1ffc2e2323eb6b238a6b6f; twid=u%3D1669820326572883969; att=1-yItAJhD6loA6BmcZQOaAg29cbfdzsfUlNWwUvR7a; personalization_id="v1_OjUERdLRXwlznWtmCNrHJg=="',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/home',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': fixed_user_agent,
            'x-client-uuid': '90c9b883-a013-48f4-a9c7-8934609f80e4',
            'x-csrf-token': twitter_session.cookies['ct0'],
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
        }

        # print(f'x-csrf-token = > {twitter_session.cookies["ct0"]}')

        with twitter_session as s:
            # contents_info = s.post(url, json=params, headers=headers).json()
            # pp(contents_info)
            res = s.post(url, json=params, headers=headers)
            if res.ok:
                print(f"\n성공 code:{res.status_code}")
                df["tweet"].values[idx] = 'O'
                df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
            else:
                print(f"\n실패 code:{res.status_code} reason:{res.reason} msg:{res.text}")
                df["tweet"].values[idx] = 'X'
                df.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)

        message = ''

        today_date = str(datetime.datetime.now())
        today_date = today_date[:today_date.rfind(
            ':')].replace('-', '.')
        print(f'현재 시간: ', today_date)
        print(
            f'다음 시작 시간: {strftime("%H:%M:%S", gmtime(TWEET_WRITE_WAIT_TIME))} 이후 다시 실행 됩니다.\n')
        sleep(TWEET_WRITE_WAIT_TIME)


# main start
def main():
    try:
        start_time = time.time()  # 시작 시간 체크
        now = datetime.datetime.now()
        print("START TIME : ", now.strftime('%Y-%m-%d %H:%M:%S'))
        print("\nSTART...")

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 시작]', C_END)
        driver = init_driver()
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 완료]', C_END)

        while True:
            print(
                f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}우선 워드프레스 리스트를 먼저 저장하고 원하는 플랫폼(트위터)에 해당 링크들을 백링크하는 방식입니다.{C_END}')
            print('\n워드프레스 포스팅 리스트를 받아오시려면' + C_BOLD +
                  C_RED + ' (1)' + C_END + '번을 눌러주시고,')
            print('가져온 포스팅 리스트들을 본인 트위터에 백링크하고 싶다면' + C_BOLD +
                  C_RED + ' (2)' + C_END + '번을 눌러주시고,')
            print('프로그램을 종료하고 싶으면' + C_BOLD +
                  C_RED + ' (q)' + C_END + '를 눌러주세요')

            input_num = input('원하는 번호를 입력하세요 : ')
            if input_num == 'q':
                break

            if input_num == '1':
                print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}워드프레스 포스팅 리스트를 가져오기 시작{C_END}')
                get_wordpress_post_lists()
                print(
                    f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}워드프레스 포스팅 리스트를 가져와 ({csv_save_path})로 저장하는데 성공하였습니다.{C_END}')

            elif input_num == '2':
                print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}본인 트위터 에 백링크 글 쓰기 시작{C_END}')
                twitter_backlink_post(driver)
                print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}본인 트위터 에 백링크 글 쓰기 완료{C_END}')

            else:
                print("잘못 입력 하였습니다. 1, 2, q 중에서 선택하시기 바랍니다.")
                continue

    finally:
        end_time = time.time()  # 종료 시간 체크
        ctime = end_time - start_time
        time_list = str(datetime.timedelta(seconds=ctime)).split(".")
        print("실행시간 (시:분:초)", time_list)
        now = datetime.datetime.now()
        print("END TIME : ", now.strftime('%Y-%m-%d %H:%M:%S'))
        print("\nEND...")


# main end
if __name__ == '__main__':
    main()
