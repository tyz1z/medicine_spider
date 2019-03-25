import requests
from mongoLink import connection,get_collection,info_model
import random
import logging
from httputil import get_response,return_soup
from engine import workshop,base_task
import re

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

origin_url = 'http://www.way2healthcare.com/way2medicine'
front_url = 'http://www.way2healthcare.com/'


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

cli = connection()
coll = get_collection(cli, "india", "info_div50_1")  
info_map = {"brand_name": "Brand Name", "dosage_form": "Dosage Form", "company_name":"Company Name","packing": "Packaging", "molecule": "Molecule", "category": "Category", "strength": "Strength","mrp_rs": "MRP(Rs)"}

india_model = info_model(coll, info_map)
  
def save(name,dosage,company,packing,molecule,category,strength,mrp):
    p = india_model.get_piece(brand_name=name, dosage_form=dosage, company_name=company,packing=packing, molecule=molecule, category=category, strength=strength,mrp_rs=mrp)
    p.save()   
    
def deal(html):
    pattern = re.compile(r'.*?medicine\(\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\);',re.S)
    #print(html)
    soup = return_soup(html)
    tables = soup.select('#no-more-tables > table > tbody > tr > .cur_poi')
    for table in tables:
        try:
            result = re.findall(pattern, table['onclick'])
            for i in result[0]:
                i = i.replace(' ','').replace('\n','').replace('\t','').replace('\r','')
            save(*result[0])
        except Exception as e:
            print(e)
            logger.error('phrase error',exc_info=True)
            logger.info('phrase error,the origin tag is: '+str(table))
            return False
    return True

class india_task(base_task):
    def __init__(self,page,*args,**kw):
        self.url = "http://www.way2healthcare.com/way2medicine?&per_page="+str(page)
        self.page = page
        super(india_task,self).__init__(*args,**kw)
        
    def run(self):
        html = get_response(self.url)
        if not html:
            logger.error('failed to requests: '+self.url)
            return False
        succeed = deal(html)
        return succeed 

def sleep_time():
    return random.randint(2,5)
    
def main():
    ws = workshop(1,sleep_time)
    for i in range(50):
        ws.add_task(india_task(i+1,ws),0)
    #ws.check()
    #ws.set_test_mode(50)
    ws.run()
    
    logger.info('these should be figure out: ' + str(ws.failed_queue))
    logger.info('finished')

if __name__ == '__main__':
    main()

