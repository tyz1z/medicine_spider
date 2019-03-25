# -*- coding: utf-8 -*-
import scrapy
import re
from russia.items import RussiaItem
from time import sleep
from tqdm import tqdm
import logging
logger = logging.getLogger(__name__)

# a:1-4
# b:1-3
# v:1-2

class VidalSpider(scrapy.Spider):
    name = 'vidal'
    allowed_domains = ['www.vidal.ru']

    start_urls = ['https://www.vidal.ru/drugs/products/p/rus-a?p=2', 'https://www.vidal.ru/drugs/products/p/rus-a?p=3', 'https://www.vidal.ru/drugs/products/p/rus-a?p=4', 'https://www.vidal.ru/drugs/products/p/rus-a',
                  'https://www.vidal.ru/drugs/products/p/rus-b?p=2', 'https://www.vidal.ru/drugs/products/p/rus-b?p=3', 'https://www.vidal.ru/drugs/products/p/rus-b',
                  'https://www.vidal.ru/drugs/products/p/rus-v?p=2', 'https://www.vidal.ru/drugs/products/p/rus-v',
                  'https://www.vidal.ru/drugs/products/p/rus-g?p=2', 'https://www.vidal.ru/drugs/products/p/rus-g?p=3', 'https://www.vidal.ru/drugs/products/p/rus-g',
                  'https://www.vidal.ru/drugs/products/p/rus-d?p=2', 'https://www.vidal.ru/drugs/products/p/rus-d',
                  'https://www.vidal.ru/drugs/products/p/rus-e',
                  'https://www.vidal.ru/drugs/products/p/rus-zh',
                  'https://www.vidal.ru/drugs/products/p/rus-z',
                  'https://www.vidal.ru/drugs/products/p/rus-i?p=2', 'https://www.vidal.ru/drugs/products/p/rus-i',
                  'https://www.vidal.ru/drugs/products/p/rus-j',
                  'https://www.vidal.ru/drugs/products/p/rus-k?p=2','https://www.vidal.ru/drugs/products/p/rus-k?p=3', 'https://www.vidal.ru/drugs/products/p/rus-k?p=4', 'https://www.vidal.ru/drugs/products/p/rus-k',
                  'https://www.vidal.ru/drugs/products/p/rus-l?p=2', 'https://www.vidal.ru/drugs/products/p/rus-l',
                  'https://www.vidal.ru/drugs/products/p/rus-m?p=2', 'https://www.vidal.ru/drugs/products/p/rus-m?p=3','https://www.vidal.ru/drugs/products/p/rus-m',
                  'https://www.vidal.ru/drugs/products/p/rus-n?p=2', 'https://www.vidal.ru/drugs/products/p/rus-n',
                  'https://www.vidal.ru/drugs/products/p/rus-o',
                  'https://www.vidal.ru/drugs/products/p/rus-p?p=2', 'https://www.vidal.ru/drugs/products/p/rus-p?p=3', 'https://www.vidal.ru/drugs/products/p/rus-p',
                  'https://www.vidal.ru/drugs/products/p/rus-r?p=2', 'https://www.vidal.ru/drugs/products/p/rus-r',
                  'https://www.vidal.ru/drugs/products/p/rus-s?p=2', 'https://www.vidal.ru/drugs/products/p/rus-s?p=3', 'https://www.vidal.ru/drugs/products/p/rus-s',
                  'https://www.vidal.ru/drugs/products/p/rus-t?p=2', 'https://www.vidal.ru/drugs/products/p/rus-t?p=3','https://www.vidal.ru/drugs/products/p/rus-t',
                  'https://www.vidal.ru/drugs/products/p/rus-u',
                  'https://www.vidal.ru/drugs/products/p/rus-f?p=2', 'https://www.vidal.ru/drugs/products/p/rus-f',
                  'https://www.vidal.ru/drugs/products/p/rus-h',
                  'https://www.vidal.ru/drugs/products/p/rus-ts?p=2', 'https://www.vidal.ru/drugs/products/p/rus-ts',
                  'https://www.vidal.ru/drugs/products/p/rus-ch',
                  'https://www.vidal.ru/drugs/products/p/rus-sh',
                  'https://www.vidal.ru/drugs/products/p/rus-eh?p=2', 'https://www.vidal.ru/drugs/products/p/rus-eh',
                  'https://www.vidal.ru/drugs/products/p/rus-yu',
                  'https://www.vidal.ru/drugs/products/p/rus-ya',
                  'https://www.vidal.ru/drugs/products/p/5',
                  'https://www.vidal.ru/drugs/products/p/9',
                  'https://www.vidal.ru/drugs/products/p/l']


    def start_requests(self):

        for i in (self.start_urls):
            self.logger.info('start to parse %s',i)
            yield scrapy.Request(i,self.parse)

    def parse(self, response):
        detail_list = self.parse_letter_page(response)

        for i in detail_list:
            self.logger.info('start to parse detail page %s',i)
            yield scrapy.Request(i,callback=self.parse_detail)





    def parse_letter_page(self, response):
        detail_urls = response.css('#vidal table .products-table-name a::attr(href)').extract()
        self.logger.info('get all the url in %s',response.url)
        for url in detail_urls:
            yield response.urljoin(url) # return urls generator object


    def select_item(self,rule,response,isCss):
        try:
            if isCss:
                result = ''
                total_list = response.css(rule).extract()
                for item in total_list:
                    result += item
                    result += ','
                return result.replace('\n','').replace('\t','').rstrip(',')
            else:
                result = ''
                total_list = response.xpath(rule).extract()
                if len(total_list)==1:return total_list[0]
                else:
                    for item in total_list:
                        result += item
                        result += ' '
                return result
        except:
            result = None
            return result

    def format_word(self,rule,string):
        if string:
            temp_list = re.findall(rule,string)
            result = ''
            for word in temp_list:
                result += word
                result += ' '
            return result
        else:
            return None

    def format_table_tag_p(self,rule,list):
        origin = ''
        if not list:
            return None
        elif len(list) == 1:
            return list[0]
        else:
            for i in list:
                if '</table>' in i:
                    origin += i
                else:
                    part = re.findall(rule,i)
                    if part:
                        try:
                            origin += part[0].replace('\n','').replace('\t','')
                        except Exception:
                            self.logger.warning('call for fotmat_table_tag_p failed, the list is %s',str(list))
                    else:
                        pass
            return origin


    def parse_detail(self, response):
        item = RussiaItem()

        # init the params
        program = None
        storage_time = None
        storage = None
        pha_sale = None
        med_inter = None
        excess = None
        s_eff = None
        influence = None
        active_ing = None
        phar = None

        pattern_name = re.compile('.*?an>(.*?)</span>.*?',re.S)
        pattern_per_NO = re.compile('.*?>.*?:(.*?)от.*?',re.S)
        pattern_per_NO_without_shit = re.compile('.*?>.*?:(.*?)<.*?',re.S)

        pattern_re_per = re.compile('.*?:(.*?)</span>',re.S)

        pattern_active_ulli = re.compile('<a.*?>(.*?)</a>.*?<span.*?>(.*?)</span>',re.S)
        pattern_sup = re.compile('.*?:(.*?)</p>',re.S)

        # 该正则用于去除空格，并选中非空格
        pattern_clinical = re.compile('\s+(\S+.*?)',re.S)

        # 该正则用于在构造特殊事项时取出 <b> 标签的值
        pattern_select_tag_b = re.compile('.*?<b>(.*?)</b>',re.S)

        pattern_tag = re.compile('.*?>(.*?)</.*?',re.S)
        pattern_p_tag = re.compile('.*?p>(.*?)</p>.*?',re.S)
        pattern_lis_url = re.compile('<a.*?"(.*?)".*?')
        pattern_for_bad_content = re.compile('.*?block-content">(.*?)</div>.*?',re.S)
        pattern_for_ban_id = re.compile('.*?block-head">(.*?)<.*?',re.S)
        licensee = self.select_item('.owners a::text',response,1)
        licensee = self.format_word(pattern_clinical,licensee)
        producer = self.select_item('.distributor a::text',response,1)
        producer = self.format_word(pattern_clinical,producer)
        atx = self.select_item('#atc_codes .block-content a::text',response,1)
        atx = self.format_word(pattern_clinical,atx)

        med = self.select_item('#phthgroup .block-content a::text',response,1)


        formulation = self.select_item('#products tr td.products-table-zip div::text', response, 1)
        per_NO = str(response.css('#products tr td.products-table-zip span').extract())

        try:
            if 'от' in per_NO:
                per_NO = re.findall(pattern_per_NO,per_NO)[0].replace('\\n','').replace('\\t','')
            else:
                per_NO = re.findall(pattern_per_NO_without_shit,per_NO)[0].replace('\\n','').replace('\\t','')
        except Exception:
            self.logger.warning('failed to format the per_NO,the url is %s',response.url)
            pass
        exterior = ''
        sup = None


        table_in_exterior = response.xpath('//div[@id="composition"]/div[@class="block-content composition"]/table').extract()

        influence_list = response.xpath('//div[@id="influence"]/div[@class="block-content"]/node()').extract()
        try:
            influence = self.format_table_tag_p(pattern_tag,influence_list)
        except Exception:
            self.logger.warning('failed to format the influence, the url is %s',response.url)
            pass

        med_inter_list = response.xpath('//div[@id="interaction"]/div[@class="block-content"]/node()').extract()
        try:
            med_inter = self.format_table_tag_p(pattern_p_tag,med_inter_list)
        except Exception:
            self.logger.warning('failed to format the medicine_inter, the url is %s', response.url)
            pass

        pha_sale_list = response.xpath('//div[@id="pharm"]/div[@class="block-content"]/node()').extract()
        try:
            pha_sale = self.format_table_tag_p(pattern_p_tag, pha_sale_list)
        except Exception:
            self.logger.warning('failed to format the pha_sale, the url is %s', response.url)
            pass

        ind_list = response.xpath('//div[@id="indication"]/div[@class="block-content"]/node()').extract()
        ind = None
        try:
            if ind_list:
                ind = ''
                for i in ind_list:
                    ind += self.format_word(pattern_clinical,i)
        except Exception:
            self.logger.warning('failed to format the ind, the url is %s',response.url)
            pass


        phar_list = response.xpath('//div[@id="kinetics"]/div[@class="block-content"]/node()').extract()
        try:
            phar = self.format_table_tag_p(pattern_tag,phar_list)
        except Exception:
            self.logger.warning('failed to format the phar, the url is %s',response.url)
            pass


        clinical = response.css('#clphgroup .block-content a::text').extract()
        try:
            if clinical:
                clinical = self.format_word(pattern_clinical,clinical[0])
        except Exception:
            self.logger.warning('failed to format the clinical, the url is %s',response.url)
            pass

        select_exterior = response.xpath('//div[@id="composition"]/div[@class="block-content composition"]/p').extract()
        for i in select_exterior:
            if 'Вспомогательные вещества' in i:
                try:
                    sup = re.findall(pattern_sup,i)[0]
                except Exception:
                    self.logger.warning('failed to format the sup, the url is %s',response.url)
                    pass
            exterior += i
        try:
            if table_in_exterior:
                exterior += table_in_exterior[0]
        except Exception:
            self.logger.warning('failed to deal with table of exterior, the url is %s',response.url)
            pass

        s_eff_list = response.xpath('//div[@id="side_effects"]/div[@class="block-content"]/node()').extract()
        try:
            s_eff = self.format_table_tag_p(pattern_tag, s_eff_list)
        except Exception:
            self.logger.warning('failed to format the side effect, the url is %s',response.url)
            pass


        excess_list = response.xpath('//div[@id="over_dosage"]/div[@class="block-content"]/node()').extract()
        try:
            excess = self.format_table_tag_p(pattern_tag, excess_list)
        except Exception:
            self.logger.warning('failed to format the excess, the url is %s',response.url)
            pass


        storage_list = response.xpath('//div[@id="storage_conditions"]/div[@class="block-content"]/node()').extract()
        try:
            storage = self.format_table_tag_p(pattern_p_tag, storage_list)
        except Exception:
            self.logger.warning('failed to format the storage, the url is %s',response.url)
            pass


        storage_time_list = response.xpath('//div[@id="storage_time"]/div[@class="block-content"]/node()').extract()
        try:
            storage_time = self.format_table_tag_p(pattern_p_tag, storage_time_list)
            storage_time = self.format_word(pattern_clinical,storage_time)
        except Exception:
            self.logger.warning('failed to format the storage_time, the url is %s',response.url)
            pass


        program_list = response.xpath('//div[@id="dosage"]/div[@class="block-content"]/node()').extract()
        try:
            program = self.format_table_tag_p(pattern_p_tag,program_list)
            program = self.format_word(pattern_clinical,program)
        except Exception:
            self.logger.warning('failed to format the program, the url is %s',response.url)
            pass

        # 禁忌的id一定是contra
        next_id = None

        # 遍历一遍导航以得知禁忌是否存在
        ban_exist = 0
        lis = response.xpath('//div[@class="navigation"]/div[@class="navigation-items"]/div/a').extract()
        if lis:
            for index,li in enumerate(lis):
                if '#contra' in li:
                    ban_exist = 1
                    try:
                        # 从总标题索引处找到禁忌的下一个索引，但其本身可能就是最后一个索引，因此这里需要用try包住
                        next_id = re.findall(pattern_lis_url,lis[index+1])[0]
                        # print(next_id)
                    except Exception:
                        self.logger.info('this medicine hasn\'t ban_items')
                        pass
                else:
                    pass


        # 标记从哪里开始出现小标题及其对应的内容
        start_index = 0

        # ban_dic 为一字典，存放禁忌事项
        ban_dic = {}

        total_page = response.xpath('//div[@class="more-info"]/node()').extract()
        try:
            if total_page and ban_exist:
                # 确定哪里是起点
                for index, part in enumerate(total_page):
                    if 'id="contra"' in part:
                        start_index = index
                        break
                    else:
                        pass
                #确定起点是否同时也是终点
                if not next_id:
                    try:
                        value = re.findall(pattern_for_bad_content, total_page[index])[0]
                        ban_dic['Противопоказания к применению'] = value
                    except Exception:
                        self.logger.warning('failed to build the ban_dic,the url is %s',response.url)
                        pass
                # 从起点+1开始解析，先拿key
                else:
                    for part in total_page[start_index + 1:]:
                        # 如果 next_id 存在且序号已经到达了特殊事项，那么退出，不继续读取
                        if next_id:
                            if ('id="%s"' % next_id[1:]) in part:
                                break
                        else:
                            pass
                        id = re.findall(pattern_for_ban_id, part)
                        # 假如key拿到，那么拿value。注意key不能含有.
                        if id:
                            id = id[0].replace('.','')
                            value = re.findall(pattern_for_bad_content, part)[0]
                            # 拿到value后，赋值进字典
                            ban_dic[id] = value
        except Exception:
            self.logger.warning('failed to format the ban dic,the url is %s',response.url)
            pass


        # 特殊事项也需要构造为字典形式，其id也必是 special，
        # 但特殊事项同属同一结构，可以直接用xpath选中

        total_p = response.xpath('//div[@id="special"]/div[@class="block-content"]/p').extract()

        special_dic = {}

        # 用于标记当前行是否应该作为字典的value
        status = 0

        try:
            if total_p:
                # 由于标题一定是加粗的，因此用 b 标签选中并作为key，此时key所在行已经没有其他内容，pass
                for index,i in enumerate(total_p):
                    if '<b>' in i:
                        status = 1
                        key = re.findall(pattern_select_tag_b,i)[0].replace('.','')
                        # 注意，key中不能含有点，字符串替换一遍
                        pass
                # 若status标识为真，说明已经拿到了key，下面全是对应的value
                    if status:
                        if key not in special_dic:
                            special_dic[key] = re.findall(pattern_p_tag, i)[0]
                        else:
                            special_dic[key] += re.findall(pattern_p_tag, i)[0]
                # 否则说明该段并没有直接的子标题，只有唯一标题special
                    else:
                        if 'special' not in special_dic:
                            special_dic['Особые указания'] = str(i)
                        else:
                            special_dic['Особые указания'] += str(i)
        except Exception:
            self.logger.warning('failed to build the special item, the url is %s',response.url)
            pass




        # 再注册
        re_per = response.css('#products tr td.products-table-zip span').extract()

        for check_exist_re_per in re_per:
            if 'Дата перерегистрации' in check_exist_re_per:
                try:
                    re_per = re.findall(pattern_re_per,check_exist_re_per)[0]
                except Exception:
                    self.logger.warning('success match with re_per tag, but faild to parse it, url is %s',response.url)
            else:
                re_per = None

        judge = response.xpath('//div[@itemprop="articleBody"]/div[@class="block"]/ul/li').extract()

        if judge:
            try:
                # it has ul/li
                active_ing = []
                for i in judge:
                    # nums_i equal to how many li tag
                    part_list = re.findall(pattern_active_ulli,i)[0]
                    part = ''
                    for j in part_list:
                        # j only exist 2,that's like -> j(j2)
                        part += j
                    active_ing.append(part)
            except Exception:
                self.logger.warning('failed to bulid the active_ing item, the url is %s',response.url)
                pass

        else:
            # means that this page of active_ing isn't ul/li
            active_ing_A = self.select_item('//div[@itemprop="articleBody"]/div[@class="block"]/a/text()',response,0)
            active_ing_B = self.select_item('//div[@itemprop="articleBody"]/div[@class="block"]/span[@class="small"]/text()',response,0)
            try:
                active_ing = active_ing_A+active_ing_B
            except Exception:
                self.logger.warning('failed to bulid the active_ing, the url is %s',response.url)
                pass



        name = response.xpath('//div[@class="breadcrumbs"]/span').extract()
        try:
            name = re.findall(pattern_name,str(name))[0]
        except Exception:
            self.logger.warning('failed to parse the medicine name, the url is %s',response.url)

        item['program'] = program
        item['special'] = special_dic
        item['storage_time'] = storage_time
        item['storage'] = storage
        item['pha_sale'] = pha_sale
        item['med_inter'] = med_inter
        item['excess'] = excess
        item['s_eff'] = s_eff
        item['influence'] = influence
        item['med'] = med
        item['clinical'] = clinical
        item['re_per'] = re_per
        item['name'] = name
        item['licensee'] = licensee
        item['producer'] = producer
        item['atx'] = atx
        item['active_ing'] = active_ing
        item['formulation'] = formulation
        item['per_NO'] = per_NO
        item['sup'] = sup
        item['exterior'] = exterior
        item['phar'] = phar
        item['ind'] = ind
        item['ban'] = ban_dic
        # print(item)
        yield item
        pass
