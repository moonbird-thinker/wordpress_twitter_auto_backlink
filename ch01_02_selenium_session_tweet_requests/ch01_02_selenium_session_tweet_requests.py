
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
import subprocess
import platform
from time import sleep
from tqdm import tqdm
import requests
osName = platform.system()

LOADING_WAIT_TIME = 5
LOGIN_WAIT_TIME = 180  # 트위터 로그인시 기다리는 시간

fixed_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Whale/3.19.166.16 Safari/537.36'

def init_driver():
    # try :
    #     shutil.rmtree(r"C:\chrometemp23")  #쿠키 / 캐쉬파일 삭제(캐쉬파일 삭제시 로그인 정보 사라짐)
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
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9224")  # 디버깅 모드

    # service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\118.0.5993.71\\chromedriver.exe')
    service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\119.0.6045.106\\chromedriver.exe')
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
            for x in range(LOGIN_WAIT_TIME):  # 180
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
        print(f"{cookie['name']} = {cookie['value']}")

    _session = requests.Session()
    
    headers = {
        'User-Agent': fixed_user_agent,
    }
    print(f'\n{_session.headers}')
    print(f'\n{_session.cookies}')

    _session.headers.update(headers)  # User-Agent 변경
    print(f'\n{_session.headers}')

    _session.cookies.update(cookie_dict)  # 응답받은 cookies로  변경
    print(f'\n{_session.cookies}')

    _cookies = driver.get_cookies()
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
        print(f"{cookie['name']} = {cookie['value']}")

    return _session
    

def write_twitter(session):

    headers = {
        'authority': 'twitter.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'content-type': 'application/json',
        # 'cookie': '_ga=GA1.2.1000355156.1698520932; g_state={"i_l":0}; _gid=GA1.2.145289027.1700488117; guest_id=v1%3A170048899760902758; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCALtCu2LAToMY3NyZl9p%250AZCIlMzQ3NWMyYjAzZjJjZjVmOTkwNDllNjE3MjU2YjFiNDE6B2lkIiU4ZGU1%250AMTlhMGE1MTlkMzBjYWJlN2YyZDUxYThkNjdiZg%253D%253D--8a2cd1d8ecffeaa6eb34e91ed2bfaf5611d6f1b6; kdt=zmxfGdX3biFgM0nRnvegJMhCbz1jqCSdDhnA010A; auth_token=8b1c8d8f21fece36163e7a1f4422276d1934fac9; ct0=d1f76e5ee6e6144da3974b635079d1a6ca4fed29ec10c2cb1ba66e59add746ebf6f4f5884103bed44942175b2a33466b30f5a9244f466a240dff2e413c12ef9e392ee2e19852fa3531c210e9f4cd7b25; guest_id_ads=v1%3A170048899760902758; guest_id_marketing=v1%3A170048899760902758; lang=en; twid=u%3D1633456808609349635; att=1-nzWMpt7DWMiTGmBtRqh0AiT1IxM0l1GEca3uC4v1; personalization_id="v1_w2KJS0oLWx1jx2byOeHUkA=="',
        'origin': 'https://twitter.com',
        'referer': 'https://twitter.com/compose/tweet',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-client-transaction-id': 'fDFMBEOQofFN6a1DZM9zMeOageqcUzZ22TP9qdaLC7m8OTNIOE40GiFykrfLmqibIap/cH1QkPo5kKIAdo44u/obFawgfQ',
        'x-client-uuid': '60945c9e-6912-4606-91ad-22860c7bdb7d',
        'x-csrf-token': session.cookies['ct0'],
        'x-twitter-active-user': 'yes',
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-client-language': 'en',
    }

    params = {
        'variables': {
            'tweet_text': '오늘 너무 수고했네요!!!!!',
            'dark_request': False,
            'media': {
                'media_entities': [],
                'possibly_sensitive': False,
            },
            'semantic_annotation_ids': [],
        },
        'features': {
            'c9s_tweet_anatomy_moderator_badge_enabled': True,
            'tweetypie_unmention_optimization_enabled': True,
            'responsive_web_edit_tweet_api_enabled': True,
            'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
            'view_counts_everywhere_api_enabled': True,
            'longform_notetweets_consumption_enabled': True,
            'responsive_web_twitter_article_tweet_consumption_enabled': False,
            'tweet_awards_web_tipping_enabled': False,
            'responsive_web_home_pinned_timelines_enabled': True,
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
        'queryId': '5V_dkq1jfalfiFOEZ4g47A',
    }
    
    url = 'https://twitter.com/i/api/graphql/5V_dkq1jfalfiFOEZ4g47A/CreateTweet'
    
    with session as s:
        res = s.post(url, json=params, headers=headers)
    print(res)



# main start
if __name__ == '__main__':
    try:
        print("\nSTART...")
        driver = init_driver()
        sleep(1)
        
        ## 트위터 로그인
        twitter_login(driver)
        sleep(1)
        
        ## 트위터 로그인 정보로 driver 객체를 사용해서 트위터 세션(쿠키 > session) 정보를 받아온다
        twitter_session = get_cookies_session(driver, 'https://twitter.com/home')
        
        ## 트위터에 안녕하세요 쓰기
        write_twitter(twitter_session)
    
    finally:
        # driver.close() # 마지막 창을 닫기 위해서는 해당 주석 제거
        # driver.quit()
        print("\nEND...")
