import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import sql_queries as queries


class Parser:
    """
    The main class containing common functions for all parsers,
    intended for other parser classes to inherit from it.
    """

    def __init__(self, list_url):
        """
        Initialization of the class object.

        :param list_url: The static url prefix of the pages to be parsed.
        """
        self.list_url = list_url
        self.source = None
        self.conn = sqlite3.connect('./data/news.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """
        Creates database tables if they don't exist.
        """
        self.cursor.execute(queries.create_table_sources)
        self.cursor.execute(queries.create_table_articles)
        self.conn.commit()

    def _get_source(self):
        """
        Gets the `id` of the source used by parser from the database.
        If the source is not in database, creates one.
        """
        name = '/'.join(self.list_url.split('/')[:3])

        self.cursor.execute(queries.select_from_sources, (name,))
        row = self.cursor.fetchone()

        if row:
            self.source = row[0]
        else:
            self.cursor.execute(queries.insert_in_sources, (name,))
            self.conn.commit()
            self.source = self.cursor.lastrowid

    def _write_to_db(self, values):
        """
        Writes the data to the `articles` table in database.

        :param values: List of values for database enty (link, 
                       title, text, date, source_id).
        """
        self.cursor.execute(queries.insert_in_articles, values)
        self.conn.commit()

    def _fetch_page(self, url):
        """
        Gets the html content of the web page.

        :param url: The url of the page.
        :return soup: The object containing html content.
        """
        try:
            response = requests.get(url)

            if response.status_code != 200:
                print(f'Error: code {response.status_code} on {url}')
                raise ValueError
            
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f'Error on _fetch_page: {e}')
            return
        
    def _date_to_url(self, date):
        """
        Transforms the date in order to use it in the page url.

        :param date: The datetime object.
        :return string: The date in the format required by the parser.
        """
        pass
        
    def _get_list(self, url):
        """
        Gets the list of article titles and links from the web page.

        :param url: The url of the page for parsing.
        :return list: The list of tuples in format [(title, href)].
        """
        pass

    def _get_article(self, url):
        """
        Gets the text of the article.

        :param url: The url of the page for parsing.
        :return text: The text of the article.
        """
        pass

    def _save_articles_from_list(self, list, date):
        """
        Gets texts from all articles in the provided list and writes
        them to database.

        :param list: The list of tuples in format [(title, href)].
        :param date: The date corresponding to the articles.
        """
        for (title, href) in list:
            text = self._get_article(href)
            if text == '': continue

            values = [href, title, text, date, self.source]
            self._write_to_db(values)

    def run(self, date1, date2):
        """
        Gets all the articles for the specified period of time and
        writes them to the database.

        :param date1: Start date.
        :param date2: End date.
        """
        start = datetime.strptime(date1, '%d.%m.%Y')
        end = datetime.strptime(date2, '%d.%m.%Y')

        current = start
        while current <= end:
            print(f'Source: {self.source}. Date: {current}.')
            url = self._date_to_url(current)
            a_list = self._get_list(url)
            self._save_articles_from_list(a_list, current)
            current += timedelta(days=1)

        self.conn.close()
        print(f'Source {self.source} finished!')

class UkrPravdaParser(Parser):
    def __init__(self, list_url):
        super().__init__(list_url)
        self._get_source()

    def _date_to_url(self, date):
        return date.strftime('%d%m%Y')

    def _get_list(self, url):
        soup = self._fetch_page(f'{self.list_url}{url}')
        if not soup: return []
    
        data = []
        tags = soup.find_all('div', class_='article_news_bold')
        for tag in tags:
            tag = tag.a
            title = tag.find_all(string=True, recursive=False)
            href = tag['href']
            href = f'https://www.pravda.com.ua{href}'
            data.append((title[0], href))

        return data
    
    def _get_article(self, url):
        soup = self._fetch_page(url)
        if not soup: return ''

        data = ''
        text = soup.find('div', class_='post_text')
        ps = text.find_all('p')
        for p in ps:
            data += p.text
        
        return data

class UnianParser(Parser):
    def __init__(self, list_url):
        super().__init__(list_url)
        self._get_source()

    def _date_to_url(self, date):
        return date.strftime('%Y%m%d')

    def _get_list(self, url):
        soup = self._fetch_page(f'{self.list_url}{url}')
        if not soup: return []
    
        data = []
        tags = soup.find_all('h3')
        for tag in tags:
            tag = tag.a
            title = tag.find_all(string=True, recursive=False)
            href = tag['href']
            data.append((title[0], href))

        return data
    
    def _get_article(self, url):
        soup = self._fetch_page(url)
        if not soup: return ''

        breadcrumbs = soup.find('div', class_='breadcrumbs')
        if not breadcrumbs: return ''

        items = breadcrumbs.find_all('li')
        permitted = [' Війна', ' Світ', ' Українa', ' Зброя']
        if items[2].text not in permitted: return ''

        data = ''
        text = soup.find('div', class_='article-text')
        ps = text.find_all('p')
        for p in ps:
            data += p.text
        
        return data

class TsnParser(Parser):
    def __init__(self, list_url):
        super().__init__(list_url)
        self._get_source()

    def _date_to_url(self, date):
        d = f"day={date.strftime('%d')}"
        m = f"month={date.strftime('%m')}"
        y = f"year={date.strftime('%Y')}"
        return f'{d}&{m}&{y}'

    def _get_list(self, url):
        i = 1
        data = []
        while True:
            soup = self._fetch_page(f'{self.list_url}/page-{i}?{url}')
            if not soup: break

            tags = soup.find_all('div', class_='c-card__body')
            del tags[:(len(tags) // 2)]
            permitted = ['Укрaїнa', 'Світ', 'Війна', 'Політика']

            for tag in tags:
                if not tag.footer.a: continue

                cat = tag.footer.a.text
                if cat not in permitted: continue

                tag = tag.h3.a
                title = tag.find_all(string=True, recursive=False)
                href = tag['href']
                data.append((title[0], href))
                
            i += 1
        return data
    
    def _get_article(self, url):
        soup = self._fetch_page(url)
        if not soup: return ''

        data = ''
        text = soup.find('div', class_='c-article__body')
        ps = text.find_all('p')
        for p in ps:
            data += p.text
        
        return data

class RbcParser(Parser):
    def __init__(self, list_url):
        super().__init__(list_url)
        self._get_source()

    def _date_to_url(self, date):
        return date.strftime('%Y/%m/%d')

    def _get_list(self, url):
        soup = self._fetch_page(f'{self.list_url}{url}')
        if not soup: return []

        data = []
        tags = soup.find('div', class_='newsline')
        for tag in tags.find_all('div'):
            title = tag.text
            href = tag.a['href']
            data.append((title, href))

        return data
    
    def _get_article(self, url):
        soup = self._fetch_page(url)
        if not soup: return ''

        data = ''
        text = soup.find('div', class_='txt')
        ps = text.find_all('p')
        for p in ps:
            data += p.text
        
        return data
