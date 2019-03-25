import requests
from bs4 import BeautifulSoup
import re

start_urls = ['https://www.vidal.ru/drugs/products/p/rus-a', 'https://www.vidal.ru/drugs/products/p/rus-b',
              'https://www.vidal.ru/drugs/products/p/rus-v', 'https://www.vidal.ru/drugs/products/p/rus-g',
              'https://www.vidal.ru/drugs/products/p/rus-d', 'https://www.vidal.ru/drugs/products/p/rus-e',
              'https://www.vidal.ru/drugs/products/p/rus-zh', 'https://www.vidal.ru/drugs/products/p/rus-z',
              'https://www.vidal.ru/drugs/products/p/rus-i', 'https://www.vidal.ru/drugs/products/p/rus-j',
              'https://www.vidal.ru/drugs/products/p/rus-k', 'https://www.vidal.ru/drugs/products/p/rus-l',
              'https://www.vidal.ru/drugs/products/p/rus-m', 'https://www.vidal.ru/drugs/products/p/rus-n',
              'https://www.vidal.ru/drugs/products/p/rus-o', 'https://www.vidal.ru/drugs/products/p/rus-p',
              'https://www.vidal.ru/drugs/products/p/rus-r', 'https://www.vidal.ru/drugs/products/p/rus-s',
              'https://www.vidal.ru/drugs/products/p/rus-t', 'https://www.vidal.ru/drugs/products/p/rus-u',
              'https://www.vidal.ru/drugs/products/p/rus-f', 'https://www.vidal.ru/drugs/products/p/rus-h',
              'https://www.vidal.ru/drugs/products/p/rus-ts', 'https://www.vidal.ru/drugs/products/p/rus-ch',
              'https://www.vidal.ru/drugs/products/p/rus-sh', 'https://www.vidal.ru/drugs/products/p/rus-eh',
              'https://www.vidal.ru/drugs/products/p/rus-yu', 'https://www.vidal.ru/drugs/products/p/rus-ya',
              'https://www.vidal.ru/drugs/products/p/5', 'https://www.vidal.ru/drugs/products/p/9',
              'https://www.vidal.ru/drugs/products/p/l']

# start_urls = 'https://www.vidal.ru/drugs/products/p/rus-a'

pat = re.compile('\<.*?href="(.*?)">.*?',re.S)
ori = 'https://www.vidal.ru'

final = []
for j in start_urls:
    response = requests.get(j)
    # print(response.status_code)
    soup = BeautifulSoup(response.text,'lxml')
    result = []
    i = soup.select('.navigation div .page a["href"]')
    # print(i)
    for eve in i:
        # print(re.findall(pat,str(eve)))
        result.append(re.findall(pat,str(eve))[0])
    # print(result)
    # print(original)
    if result:
        for single_url in result:
            print(ori+single_url)
    # print(i)
            final.append(ori+single_url)
    else:
        pass
    final.append(j)
    print(final)
print(final)
