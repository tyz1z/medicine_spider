# -*- coding: utf-8 -*-
import scrapy
import re
import logging
logger = logging.getLogger(__name__)
from lebanon.items import LebanonItem
from tqdm import tqdm
from datetime import datetime
import html

class MophSpider(scrapy.Spider):
    name = 'moph'
    allowed_domains = ['moph.gov.lb']
    start_urls = ['http://moph.gov.lb/']

    origin = 'https://www.moph.gov.lb/en/Drugs/index/3/16928/page:'

    # test_url = ['https://www.moph.gov.lb/en/Drugs/index/3/16928/page:1','https://www.moph.gov.lb/en/Drugs/index/3/16928/page:2','https://www.moph.gov.lb/en/Drugs/index/3/16928/page:3',
    #             'https://www.moph.gov.lb/en/Drugs/index/3/16928/page:4','https://www.moph.gov.lb/en/Drugs/index/3/16928/page:5','https://www.moph.gov.lb/en/Drugs/index/3/16928/page:6',
    #             'https://www.moph.gov.lb/en/Drugs/index/3/16928/page:7','https://www.moph.gov.lb/en/Drugs/index/3/16928/page:8','https://www.moph.gov.lb/en/Drugs/index/3/16928/page:9']

    # test_url = ['https://www.moph.gov.lb/en/Drugs/index/3/16928/page:1']

    def start_requests(self):

        # 正式版
        total_pages_url = []
        for i in range(1,189):
            total_pages_url.append(self.origin+str(i))
        for page_url in tqdm(total_pages_url):
            self.logger.info('start to parse %s',page_url)
            yield scrapy.Request(page_url,self.parse)


        # 测试版
        # for i in self.test_url:
        #     self.logger.info('start to parse %s',i)
        #     yield scrapy.Request(i,self.parse)


    def parse(self, response):
        # receive a generator
        detail_page_urls = self.get_detail_page_url(response)
        for url in detail_page_urls:
            self.logger.info('start to parse detail page, url is: %s',url)
            yield scrapy.Request(url,self.parse_detail)
        pass

    def get_detail_page_url(self,response):
        match_detail_page_url = re.compile('.*?href="(.*?)".*?',re.S)
        url_container = response.xpath('//table[@class="table"]/tbody/tr').extract()

        if url_container:
            for url in url_container:
                try:
                    result = re.findall(match_detail_page_url,url)[0]
                    # if len(result) > 1:
                    #     yield response.urljoin(result[0])
                    yield response.urljoin(result)
                except Exception:
                    self.logger.warning('use re to parse url error,the origin url is %s',url)
                    pass

    def seperate_td_tag(self,string):
        seperate_td_tag = re.compile('.*?td>(.*?)</.*?', re.S)
        try:
            result = re.findall(seperate_td_tag,string)
            if result:
                return html.unescape(result[0])
            else:
                return None
        except Exception:
            self.logger.warning('seem that it failed to seperate the td tag, the string is : %s',string)
            pass

    def parse_time(self, s):
        try:
            day_s, mon_s, year_s = s.split('/')
            return datetime(int(year_s), int(mon_s), int(day_s))
        except Exception:
            self.logger.warning('failed to parse the date: %s',s)
            return None

    def parse_detail(self,response):
        item = LebanonItem()


        total_td_tag = response.xpath('//div[@class="table-responsive contentTopMargin"]/table/tbody/tr/td').extract()
        # 将所有td每19个分为一组
        dic = {}
        relate_dic = {}
        for seperate_index in range(len(total_td_tag)//19):
            # single_part 为每个分类
            single_part = total_td_tag[seperate_index*19:((seperate_index+1)*19)]
            try:
                if seperate_index == 0:
                    # 意味着这是第一个，即这个药本身md
                    item['ATC'] = self.seperate_td_tag(single_part[0])
                    item['bng'] = self.seperate_td_tag(single_part[1])
                    item['ing'] = self.seperate_td_tag(single_part[2])
                    item['code'] = self.seperate_td_tag(single_part[3])
                    item['Nb'] = self.seperate_td_tag(single_part[4])
                    item['name'] = self.seperate_td_tag(single_part[5])
                    item['dosage'] = self.seperate_td_tag(single_part[6])
                    item['pres'] = self.seperate_td_tag(single_part[7])
                    item['form'] = self.seperate_td_tag(single_part[8])
                    item['route'] = self.seperate_td_tag(single_part[9])
                    item['agent'] = self.seperate_td_tag(single_part[10])
                    item['lab'] = self.seperate_td_tag(single_part[11])
                    item['country'] = self.seperate_td_tag(single_part[12])
                    item['price'] = self.seperate_td_tag(single_part[13])
                    item['phar'] = self.seperate_td_tag(single_part[14])
                    item['stratum'] = self.seperate_td_tag(single_part[15])
                    item['party_name'] = self.seperate_td_tag(single_part[16])
                    item['party_country'] = self.seperate_td_tag(single_part[17])
                    item['date'] = self.parse_time(self.seperate_td_tag(single_part[18]))
                    # item['upper_title'] = dic

                else:
                    dic = {}
                    dic['ATC'] = self.seperate_td_tag(single_part[0])
                    dic['B/G'] = self.seperate_td_tag(single_part[1])
                    dic['Ingredients'] = self.seperate_td_tag(single_part[2])
                    dic['code'] = self.seperate_td_tag(single_part[3])
                    dic['Registration Nb'] = self.seperate_td_tag(single_part[4])
                    dic['Name'] = self.seperate_td_tag(single_part[5])
                    dic['Dosage'] = self.seperate_td_tag(single_part[6])
                    dic['Presentation'] = self.seperate_td_tag(single_part[7])
                    dic['Form'] = self.seperate_td_tag(single_part[8])
                    dic['Route'] = self.seperate_td_tag(single_part[9])
                    dic['Agent'] = self.seperate_td_tag(single_part[10])
                    dic['Laboratory'] = self.seperate_td_tag(single_part[11])
                    dic['Country'] = self.seperate_td_tag(single_part[12])
                    dic['Price'] = self.seperate_td_tag(single_part[13])
                    dic['Pharmacist Margin'] = self.seperate_td_tag(single_part[14])
                    dic['Stratum'] = self.seperate_td_tag(single_part[15])
                    dic['Responsible Party Name'] = self.seperate_td_tag(single_part[16])
                    dic['responsible Party Country'] = self.seperate_td_tag(single_part[17])
                    dic['Exch_date'] = self.parse_time(self.seperate_td_tag(single_part[18]))
                    # 剩余的应按序做成字典，key 为序号，存在 relate_dic 中
                    key = 'object'+str(seperate_index)
                    relate_dic[key] = dic
            except Exception:
                self.logger.warning('failed to assign,the origin list is %s',str(single_part))
                pass
        # 循环结束，relate_dic 已赋值完毕
        item['down_title'] = relate_dic
        yield item


