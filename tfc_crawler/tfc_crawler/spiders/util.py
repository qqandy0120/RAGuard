import requests
import json
import re
from bs4 import BeautifulSoup
# Crawling utils
def get_latest_tfc_page_id_from_db():
    path = '.src/db_info.json'
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

    return ids

def get_unprocessed_tfc_page_ids():
    page = 0
    latest_id = get_latest_tfc_page_id_from_db()
    unprocessed_ids = set()
    
    while True:
        current_ids = get_ids_from_tfc_page(page)
        print(current_ids)
        if min(current_ids) <= latest_id:
            unprocessed_ids.update(id for id in current_ids if id > latest_id)
            break

        unprocessed_ids.update(current_ids)
        page += 1
    
    return unprocessed_ids


def update_latest_tfc_page_id(new_page_id, file_path='.src/db_info.json'):
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