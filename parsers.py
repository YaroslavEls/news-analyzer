import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database.db_handler import DatabaseHandler


class Parser:
    """
    The main class containing common functions for all parsers,
    intended for other parser classes to inherit from it.
    """

    def __init__(self):
        """
        Initialization of the class object.

        :attr list_url: Url of the web resource for parsing
        :attr source: Id of the source in database
        :attr db: DatabaseHandler
        """
        self.list_url = None
        self.source = None
        self.db = DatabaseHandler()
        self.data = []

    def _get_source(self, modify=True):
        """
        Sets the source attribute to the `id` of the source
        used by parser from the database.
        If the source is not in database, creates one.
        """
        name = '/'.join(self.list_url.split('/')[:3]) \
            if modify else self.list_url

        row = self.db.get_source_id(name)

        if row:
            self.source = row[0]
        else:
            self.source = self.db.create_source(name)

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
        Writes texts from all articles in the provided list to the database.

        :param list: The list of tuples in format [(title, href)].
        :param date: The date corresponding to the articles in list.
        """
        for (title, href) in list:
            text = self._get_article(href)
            if text == '': continue

            values = [href, title, text, date, self.source]
            # self._write_to_db(values)
            self.data.append(values)

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

        self.db.disconnect()
        print(f'Source {self.source} finished!')
        return self.data

class UkrPravdaParser(Parser):
    def __init__(self):
        super().__init__()
        self.list_url = 'https://www.pravda.com.ua/news/date_'
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
    def __init__(self):
        super().__init__()
        self.list_url = 'https://www.unian.ua/news/archive/'
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
    def __init__(self):
        super().__init__()
        self.list_url = 'https://tsn.ua/news'
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
    def __init__(self):
        super().__init__()
        self.list_url = 'https://www.rbc.ua/rus/archive/'
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

class SuspilneParser(Parser):
    def __init__(self):
        super().__init__()
        self.list_url = 'https://suspilne.media/archive/'
        self._get_source()

    def _date_to_url(self, date):
        return date.strftime("%Y/%-m/%-d")

    def _get_list(self, url):
        soup = self._fetch_page(f'{self.list_url}{url}')
        if not soup: return []

        data = []
        tags = soup.find_all('div', class_='l-four-column-grid__item')
        for tag in tags:
            href = tag.a['href']
            if href.split('/')[3] in ['sport', 'culture']: continue
            title = tag.h4.text
            data.append((title, href))

        return data
    
    def _get_article(self, url):
        soup = self._fetch_page(url)
        if not soup: return ''

        text = soup.find('div', class_='l-article-content__container-inner')
        data = text.find('h2').text if text.find('h2') else ''
        ps = text.find_all('p')
        for p in ps:
            data += p.text
        
        return data

class TelegramParser(Parser):
    def __init__(self, name, post_id):
        super().__init__()
        self.list_url = f'https://t.me/s/{name}'
        self._get_source(modify=False)
        self.post_id = post_id

    def _date_to_url(self, date):
        return date

    def _get_list(self, date):
        data = []
        stop = 0
        while stop == 0:
            soup = self._fetch_page(f'{self.list_url}/{self.post_id}')
            if not soup: return []

            name = self.list_url.split('/')[4]
            nums = [x for x in range(int(self.post_id)-2, int(self.post_id)+3)]
            tags = [
                soup.find('div', {
                    'class': 'tgme_widget_message', 
                    'data-post': f'{name}/{i}'
                }) for i in nums
            ]
            for tag in tags:
                if not tag: continue

                title = tag.find('div', class_='tgme_widget_message_text')
                title_text = ''
                if title:
                    for br in title.find_all('br'):
                        br.replace_with('\n')
                    title_text = title.find_all(string=True, recursive=True)
                    title_text = ' '.join(title_text)
                href = f"{self.list_url}/{tag['data-post'].split('/')[1]}"

                time = tag.find('time', class_='time')['datetime']
                date_obj = datetime \
                    .strptime(time, "%Y-%m-%dT%H:%M:%S%z") \
                    .replace(minute=0, second=0, hour=0, tzinfo=None)
                if date_obj < date: 
                    continue
                if date_obj > date: 
                    stop += 1
                    continue

                data.append((title_text, href))

            self.post_id = str(int(self.post_id) + (5 - stop))

        return data
    
    def _save_articles_from_list(self, list, date):
        for (title, href) in list:
            if title == '': continue

            text = title
            title = text.split('\n')[0]
            title = title.split('.')[0] if len(title.split('.')) > 1 else title
            values = [href, title, text, date, self.source]
            # self._write_to_db(values)
            self.data.append(values)
