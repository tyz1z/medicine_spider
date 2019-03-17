import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from tqdm import tqdm
from time import sleep
import mongoLink
import random
import logging
from requests.adapters import HTTPAdapter


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
        # print(link['href'].replace(' ','%20').replace('\n',''))
        detail_url_list.append(link['href'].replace(' ','%20').replace('\n',''))
    # print(detail_url_list)
    return detail_url_list
# get_detail_url(get_origin())

# should run like this: get_detail_url(get_response(origin_url)) which will get the url list


def check_next_page(soup):
    guides = soup.select('#medicineWrapper > center > div > a')
    for guide in guides:
        if '>' == guide.text:
            # print('nextpage')
            # print(front_url+guide['href'])
            return front_url+guide['href']
    return False


# should use url_list[6] for the test
def visit_detail_page(url):
    # print(url)
    item =[]
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
                index = 1
                while index <= 15:
                    # print(table['onclick'].replace(',','').split('\'')[index])
                    item.append(table['onclick'].replace(',','').split('\'')[index])
                    index+=2
                # print(item)
                mongoLink.save(*item)
                # print('\n')
                item = []
            except Exception:
                item = []
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
    # print(url)
    item =[]
    html = get_response(url)
    if not html:
        logger.error('failed to requests: '+url)
        return
    soup = return_soup(html)
    # print(check_next_page(soup))
    tables = soup.select('#no-more-tables > table > tbody > tr > .cur_poi')
    for table in tables:
        try:
            index = 1
            while index <= 15:
                # print(table['onclick'].replace(',','').split('\'')[index])
                item.append(table['onclick'].replace(',','').split('\'')[index])
                index+=2
            #print(item)
            mongoLink.save(*item)
            # print('\n')
            item = []
        except Exception:
            item = []
            logger.error('phrase error',exc_info=True)
            logger.info('phrase error,the origin tag is: '+str(table))
            pass
    return


# visit_detail_page('http://www.way2healthcare.com/way2medicine?&category=Antacids&per_page=39')
# visit_detail_page(url_list[2])
# visit_detail_page('http://www.way2healthcare.com/way2medicine?category=Insulin%20Preparations')
# visit_detail_page('http://www.way2healthcare.com/way2medicine?&category=N.I&per_page=2')
# print(mongoLink.save())
#visit_detail_page('http://www.way2healthcare.com/way2medicine?name=INSUMAN%20RAPID')
#

def main():
    total_urls_list = get_detail_url(get_response(origin_url))
    for item in tqdm(total_urls_list):
        visit_detail_page(item)
        sleep(random.randint(2,5))

    logger.info('these should be figure out: ' + str(retry_url_list))
#retry_timeout('http://www.way2healthcare.com/way2medicine?&per_page=135')

    logger.info('finished')

if __name__ == '__main__':
    main()

