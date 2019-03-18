import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import logging


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
	
def get_response(url):
    i = 0
    while i < 5:
      try:
          print('now visit '+url)
          response = requests.get(url , headers = headers , timeout = 10)
          if response.status_code == 200:
              return response.text
          return
      except requests.exceptions.RequestException as e:
          logger.error(e)
          logger.info('requests error')
          i += 1
          return
		  
		  
def return_soup(html):
    soup = BeautifulSoup(html,'lxml')
    return soup
