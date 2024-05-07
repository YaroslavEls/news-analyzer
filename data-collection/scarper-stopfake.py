import requests
import pandas as pd
from bs4 import BeautifulSoup


n = 300
url_static = 'https://www.stopfake.org/uk/category/novyny-ua/page/'

def get_data():
    df = pd.DataFrame(columns=['page', 'text'])

    for i in range(n):
        urls = get_urls(f'{url_static}{i+1}')

        for item in urls:
            title = item.text

            if title.endswith('...'):
                url = item.find('a')['href']
                title = get_title(url)

            df = df._append({
                'page': i+1,
                'text': title
            }, ignore_index=True)

        print(f'Page {i+1} completed')

    return df

def get_urls(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Error: code {response.status_code} on {url}')
    
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find_all('h3')

def get_title(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Error: code {response.status_code} on {url}')
    
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find('h1').text


data = get_data()
data.to_csv('data.csv', index=False)
