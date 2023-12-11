from time import sleep
import os
from pathlib import Path
import pandas as pd  ## 엑셀과 같은 데이터의 조작을 쉽게 해주는 패키지
import requests
import re

wordpress_blog_address_lists = ['https://ree31206.mycafe24.com', 'https://owshopping.mycafe24.com']

def get_wordpress_post_lists():
    
    pre_df = pd.DataFrame()
    
    for address_idx, wordpress_blog_address in enumerate(wordpress_blog_address_lists):
        # print(f'{address_idx + 1}. {wordpress_blog_address}')
        
        modified_wordpress_blog_address = wordpress_blog_address.replace('https://', '').replace('http://', '').replace('.', '_')
        csv_save_path = f'{modified_wordpress_blog_address}_submit_urls.csv'
        
        if not os.path.exists(csv_save_path):
            Path(csv_save_path).touch(exist_ok=True)
        else:
            pre_df = pd.read_csv(csv_save_path)
            
        submit_urls = []
        ## jetpack sitemap.xml(sitemap-1.xml, sitemap-2.xml....) https://ree31206.mycafe24.com/sitemap-1.xml
        for i in range(2): # 0~99
            wordpress_sitemap_address = f'{wordpress_blog_address}/sitemap-{i + 1}.xml'
            # print(wordpress_sitemap_address)
            
            res = requests.get(wordpress_sitemap_address)
            if res.status_code != 200:
                break
            
            pattern = '<loc>(.*?)</loc>'
            url_info_lists = re.findall(pattern, res.text)

            for idx, url_info in enumerate(url_info_lists):
                temp_dict = {}
                print(f'{idx}. {url_info}')
                temp_dict['url'] = f'{url_info}'
                temp_dict['backlink'] = 'X'
                submit_urls.insert(0, temp_dict)  # 앞쪽에 계속 추가를 해주기 위해, sitemap 순서가 최근순이 아니기 때문에.
            
            df1 = pd.DataFrame(submit_urls, columns=['url', 'backlink'])
            
            total = pd.concat([pre_df, df1])
            
            total = total.drop_duplicates(subset=['url'], keep='first') # keep='last' first 는 위에서부터 첫값을 남기고, last면 행의 마지막 값을 남김
            
            ## + wordpress API 최근 데이터의 url을 따로 받아서 ... 
            total.to_csv(csv_save_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)


# main start
if __name__ == '__main__':
    try:
        print("\nSTART...")
    
        get_wordpress_post_lists()
        
    finally:
        print("\nEND...")