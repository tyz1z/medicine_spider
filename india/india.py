import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from tqdm import tqdm
from time import sleep
# import mongoLink
import random
import logging
import re

# a list which used to store retry urls
retry_url_list = []


origin_url = 'http://www.way2healthcare.com/way2medicine'
front_url = 'http://www.way2healthcare.com/'

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# FileHandler
file_handler = logging.FileHandler('result.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log
logger.info('Start')



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

def get_detail_url(html):
    detail_url_list = []
    soup = return_soup(html)
    sidebar_links = soup.select('.sidebar_link > li > a')
    for link in sidebar_links:
        detail_url_list.append(link['href'].replace(' ','%20').replace('\n',''))
    return detail_url_list

def check_next_page(soup):
    guides = soup.select('#medicineWrapper > center > div > a')
    for guide in guides:
        if '>' == guide.text:
            return front_url+guide['href']
    return False


# should use url_list[6] for the test
def visit_detail_page(url):

    pattern = re.compile('.*?medicine(.*?);')
    html = get_response(url)
    if not html:
        logger.error('failed to requests: '+url)
        retry_url_list.append(url)
        return
    soup = return_soup(html)
    # print(check_next_page(soup))
    while 1:
        tables = soup.select('#no-more-tables > table > tbody > tr > .cur_poi')
        for table in tables:
            try:
                print('*****')
                result = re.findall(pattern,table['onclick'])
                print(result)
            except Exception:
                logger.error('phrase error',exc_info=True)
                logger.info('phrase error,the origin tag is: '+str(table))
                pass

        next_url = check_next_page(soup)
        # print(next_url)
        if next_url:
            sleep(random.randint(2,5))
            visit_detail_page(next_url)
        break
    return

def retry_timeout(url):
    print('now dealing with '+url)
    pattern = re.compile('.*?medicine\(\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\);',re.S)
    html = get_response(url)
    if not html:
        logger.error('failed to requests: '+url)
        return
    soup = return_soup(html)
    tables = soup.select('#no-more-tables > table > tbody > tr > .cur_poi')
    for table in tables:
        try:
            print(table['onclick'])
            result = re.findall(pattern, table['onclick'])
            print(result)
            print(result[0])
            for i in result[0]:
                print(i.replace(' ','').replace('\n','').replace('\t','').replace('\r',''))
        except Exception:
            logger.error('phrase error',exc_info=True)
            logger.info('phrase error,the origin tag is: '+str(table))
            pass
    return



def main():
    total_urls_list = get_detail_url(get_response(origin_url))
    for item in tqdm(total_urls_list):
        visit_detail_page(item)
        sleep(random.randint(2,5))

    logger.info('these should be figure out: ' + str(retry_url_list))


    logger.info('finished')

if __name__ == '__main__':
    main()

