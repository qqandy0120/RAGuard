# -*- coding: utf-8 -*-
import scrapy
import re
import os
import requests
import json
import re
from bs4 import BeautifulSoup

DB_INFO_PATH = "/Users/hsiangan/Desktop/RAGuard/.src/db_info.json"

def get_latest_tfc_page_id_from_db():
    path = '/Users/hsiangan/Desktop/RAGuard/.src/db_info.json'
    with open(path, 'r') as f:
        info = json.load(f)
    assert 'latest_tfc_page_id' in info.keys(), 'Cannot fetch latest tfc page id'
    return info['latest_tfc_page_id']

# get all id in a certain page
def get_ids_from_tfc_page(page):
    BASE_URL = "https://tfc-taiwan.org.tw/articles/report"
    response = requests.get(f'{BASE_URL}?page={page}')
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html5lib')
    div_content = soup.find('div', class_='view-content')
    a_tags = div_content.find_all('a', href=re.compile(r'/articles/\d+'))
    
    ids = set([int(re.search(r'/articles/(\d+)', a_tag['href']).group(1) )for a_tag in a_tags])
    print(ids)
    return ids

def get_unprocessed_tfc_page_ids():
    page = 0
    latest_id = get_latest_tfc_page_id_from_db()
    unprocessed_ids = set()
    
    while True:
        current_ids = get_ids_from_tfc_page(page)

        if min(current_ids) <= latest_id:
            unprocessed_ids.update(id for id in current_ids if id > latest_id)
            break

        unprocessed_ids.update(current_ids)
        page += 1
    
    unprocessed_ids = sorted(list(unprocessed_ids))
    
    return unprocessed_ids

def update_latest_tfc_page_id(new_page_id, file_path=DB_INFO_PATH):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        data['latest_tfc_page_id'] = new_page_id
        
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Successfully updated latest_tfc_page_id to {new_page_id}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

class TfcSpider(scrapy.Spider):
    name = "tfc_spider"
    # Define the starting URL
    def start_requests(self):
        unprocess_pages = get_unprocessed_tfc_page_ids()
        assert unprocess_pages, "No unprocessed tfc pages."
        print(f"Unprocess Page: {unprocess_pages}")
        for page in unprocess_pages:
            url = f'https://tfc-taiwan.org.tw/articles/{page}'
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page})

    def parse(self, response):
        page_id = response.meta.get('page')
        # Check if the page exists by looking for a specific element
        if response.status == 200:
            # Extract desired content (for example, title or article text)
            title = response.xpath('//h1/text()').get()
            article = response.xpath('//div[contains(@class, "content-inner")]//text()').getall()

            # Clean up and join the article paragraphs
            article_content = ''.join(article).strip()
            # remove escaped characters
            article_content = re.sub(r'\s+', ' ', article_content).strip()
            article_content = article_content.replace('(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) {return;} js = d.createElement(s); js.id = id; js.src = "//connect.facebook.net/zh_TW/all.js#xfbml=1"; fjs.parentNode.insertBefore(js, fjs); }(document, "script", "facebook-jssdk"));', '')
            article_content = article_content.replace('<!--/*--><![CDATA[/* ><!--*/ .container { width: 80%; margin: 0 auto; .section { margin: 20px 0; padding: 20px; border: 1px solid #ccc; border-radius: 8px; background-color: #e6e7e8; } .donate-link, .bank-account { display: flex; justify-content: center; align-items: center; background-color: #e6e7e8; /* 添加背景顏色 */ text-align: center; } .qrcode { width: 150px; height: 150px; } /*--><!]]>*/ 事實查核需要你的一份力量 捐款贊助我們 本中心查核作業獨立進行，不受捐助者影響。 台灣事實查核中心捐款連結 (或掃QR Code) /接受捐助準則','')


            # Yield a dictionary with extracted data
            yield {
                'source': 'tfc-taiwan',
                'page_id': page_id,
                'title': title,
                'content': article_content
            }
            # update db_info
            update_latest_tfc_page_id(page_id)