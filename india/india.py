import requests
import mongoLink
import random
import logging

from engine import workshop,base_task


origin_url = 'http://www.way2healthcare.com/way2medicine'
front_url = 'http://www.way2healthcare.com/'



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


def get_detail_url(html):
    detail_url_list = []
    soup = return_soup(html)
    sidebar_links = soup.select('.sidebar_link > li > a')
    for link in sidebar_links:
        detail_url_list.append(link['href'].replace(' ','%20').replace('\n',''))
    return detail_url_list

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
	
def deal(html):
	soup = return_soup(html)
    tables = soup.select('#no-more-tables > table > tbody > tr > .cur_poi')
    for table in tables:
        try:
            index = 1
            while index <= 15:
                item.append(table['onclick'].replace(',','').split('\'')[index])
                index+=2
            mongoLink.save(*item)
            item = []
        except Exception:
            item = []
            logger.error('phrase error',exc_info=True)
            logger.info('phrase error,the origin tag is: '+str(table))
            return False


# visit_detail_page('http://www.way2healthcare.com/way2medicine?&category=Antacids&per_page=39')
# visit_detail_page(url_list[2])
# visit_detail_page('http://www.way2healthcare.com/way2medicine?category=Insulin%20Preparations')
# visit_detail_page('http://www.way2healthcare.com/way2medicine?&category=N.I&per_page=2')
# print(mongoLink.save())
#visit_detail_page('http://www.way2healthcare.com/way2medicine?name=INSUMAN%20RAPID')
#

class india_task(base_task):
	def __init__(self,url,*args,*kw):
		self.url = url
		super(india_task,self).__init__(*args,**kw)
		
	def run(self):
		item =[]
		html = get_response(self.url)
		if not html:
			logger.error('failed to requests: '+self.url)
			self.ws.add_task(india_task(self.url))
			return False
		succeed = deal(html)
		if succeed:
			next = check_next_page(soup)
			self.ws.add_task
		return succeed
		
	def retry(self):
		print('now dealing with '+url)
		# print(url)
		item =[]
		html = get_response(url)
		if not html:
			logger.error('failed to requests: '+url)
			return False
		succeed = deal(html)
		if succeed:
			next = check_next_page(soup)
			self.ws.add_task
		return succeed		

def sleep_time():
	return random.randint(2,5)
	
def main():
    total_urls_list = get_detail_url(get_response(origin_url))
	ws = workshop(1,sleep_time)
	for i in total_urls_list:
		ws.add_task(india_task(i,ws))
    ws.run()

    logger.info('these should be figure out: ' + str(retry_url_list))
#retry_timeout('http://www.way2healthcare.com/way2medicine?&per_page=135')

    logger.info('finished')

if __name__ == '__main__':
    main()

