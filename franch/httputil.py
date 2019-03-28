import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    
def get_response(url,get_bytes = False):
    for i in range(5):
        try:
            response = requests.get(url, headers=headers, timeout = 10)
            if response.status_code == 200:
                if get_bytes:
                    return response.content
                else:
                    return response.text
        except requests.exceptions.RequestException as e:
            logger.error(e)
            logger.info('requests error')
    return False

def post_response(url,data,get_bytes = False):
    for i in range(5):
        try:
            response = requests.post(url, data=data, headers=headers, timeout = 30)
            if response.status_code == 200:
                if get_bytes:
                    return response.content
                else:
                    return response.text
        except requests.exceptions.RequestException as e:
            logger.error(e)
            logger.info('requests error')
    return False
          
          
def return_soup(html):
    soup = BeautifulSoup(html,'lxml')
    return soup
