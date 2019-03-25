# -*- coding: utf-8 -*-
import scrapy
from tqdm import tqdm
import re
import logging
logger = logging.getLogger(__name__)
from way2h.items import Way2HItem


class IndiaSpider(scrapy.Spider):
    name = 'india'
    allowed_domains = ['way2healthcare.com']
    start_urls = ['http://http://www.way2healthcare.com/way2medicine?']
    origin = 'http://www.way2healthcare.com/way2medicine?&per_page='
    test_urls = ['http://www.way2healthcare.com/way2medicine?&per_page=1','http://www.way2healthcare.com/way2medicine?&per_page=2','http://www.way2healthcare.com/way2medicine?&per_page=3']

    retry_list = ['http://www.way2healthcare.com/way2medicine?&per_page=98','http://www.way2healthcare.com/way2medicine?&per_page=94','http://www.way2healthcare.com/way2medicine?&per_page=99',
                  'http://www.way2healthcare.com/way2medicine?&per_page=97','http://www.way2healthcare.com/way2medicine?&per_page=100','http://www.way2healthcare.com/way2medicine?&per_page=96',
                  'http://www.way2healthcare.com/way2medicine?&per_page=101','http://www.way2healthcare.com/way2medicine?&per_page=95','http://www.way2healthcare.com/way2medicine?&per_page=102',
                  'http://www.way2healthcare.com/way2medicine?&per_page=103','http://www.way2healthcare.com/way2medicine?&per_page=104','http://www.way2healthcare.com/way2medicine?&per_page=105',
                  'http://www.way2healthcare.com/way2medicine?&per_page=106','http://www.way2healthcare.com/way2medicine?&per_page=107','http://www.way2healthcare.com/way2medicine?&per_page=108',
                  'http://www.way2healthcare.com/way2medicine?&per_page=109','http://www.way2healthcare.com/way2medicine?&per_page=110','http://www.way2healthcare.com/way2medicine?&per_page=111',
                  'http://www.way2healthcare.com/way2medicine?&per_page=112','http://www.way2healthcare.com/way2medicine?&per_page=113']

    def start_requests(self):

        # 正式版
        # total_pages_url = []
        # for i in range(1, 667):
        #     total_pages_url.append(self.origin + str(i))
        # for page_url in tqdm(total_pages_url):
        #     self.logger.info('start to parse %s', page_url)
        #     yield scrapy.Request(page_url, self.parse)

        # retry
        for page_url in tqdm(self.retry_list):
            self.logger.info('start to parse %s', page_url)
            yield scrapy.Request(page_url, self.parse)


        # 测试版
        # for i in self.test_urls:
        #     self.logger.info('start to parse %s',i)
        #     yield scrapy.Request(i,self.parse)


    def parse(self, response):
        items = Way2HItem()
        td_lists = response.xpath('//table/tbody/tr/td[@class="cur_poi"]/@onclick').extract()
        patter_rule = re.compile(r'.*?medicine\(\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\,\'(.*?)\'.*?\);',re.S)
        for td in td_lists:
            try:
                result = re.findall(patter_rule,td)[0]
                items['name'] = result[0]
                items['dosage'] = result[1]
                items['company'] = result[2]
                items['packing'] = result[3]
                items['molecule'] = result[4]
                items['category'] = result[5]
                items['strength'] = result[6]
                items['MRP'] = result[7]
                yield items
            except Exception:
                self.logger.warning('failed to parse the tag %s',td)
        pass
