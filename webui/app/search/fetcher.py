"""Fetching Capability using requests"""
import logging
import requests
from bs4 import BeautifulSoup

logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('chardet').setLevel(logging.WARNING)


class Fetcher:
    """Fetching Capability using requests"""

    search_driver = None
    screenshot_driver = None

    @staticmethod
    def cleantext(soup):
        """
        Clean up the text from the extract
        :param soup:
        :return:
        """
        for script in soup(['script', 'style']):
            script.extract()  # rip it out
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = text.replace('\n', ' ')
        return text.encode('utf-8')

    @staticmethod
    def clean_string(text):
        """
        Clean up a single string
        :param text:
        :return:
        """
        try:
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text = text.replace('\n', ' ')
            return str(text)
        except TypeError:
            return text

    @staticmethod
    def read_url2(url):
        """
        Read teh supplied url
        :param url:
        :return:
        """
        # res = urlopen(url)
        # data = res.read()
        data = requests.get(url).content
        print('Fetched %s from %s' % (len(data), url))
        # if res.headers.getparam('charset').lower() != 'utf-8':
        #    data = data.encode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        print('Parsed %s from %s' % (len(data), url))
        clean_url = Fetcher.clean_string(url)
        clean_data = Fetcher.clean_string(data)

        title = soup.title.string.encode('utf-8')
        clean_text = Fetcher.cleantext(soup)
        return ([clean_url, clean_data, title, clean_text])

    @staticmethod
    def fetch_multiple(urls, top_n):
        """
        Fetch a bunch of urls
        :param urls:
        :param top_n:
        :return:
        """
        # result = Fetcher.parallel(urls, top_n)
        print(top_n)
        result = []
        for url in urls:
            result.append(Fetcher.read_url2(url))
        return result
