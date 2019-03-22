import requests
import random
import logging
from httputil import get_response,return_soup,post_response
import json
import re
from time import sleep
from engine import workshop,base_task

list_url = "http://agence-prd.ansm.sante.fr/php/ecodex/index.php#result"
origin_data ={"page":1,"cherche":1,"subsid":"","nomsubs":"","affliste":0,"listeOpen":0,"lstRecherche":"denomination","radLibelle":2,"txtCaracteres":"","txtDateDebut":"","txtDateFin":"","lstEtat":0,"lstComm":0,"lstDoc":0}

html = post_response(list_url,origin_data)
soup = return_soup(html)

sava_path = "list.json"

def getids(html):
    return re.findall(r".*specid=(.*?)'>",html)
    
def clear(html):
    pass
    
def get_drugs_and_save():
    first_html = post_response(list_url,origin_data)
    pages = re.findall(r"</b>(.*?/.*?)</td>",first_html)[0][4:]
    pages = int(pages)
    idlist = []
    idlist += getids(first_html)
    with open(sava_path,'a') as f:
        for i in range(pages):
            #sleep(1)
            origin_data['page'] = i+1
            html = post_response(list_url,origin_data)
            #idlist += getids(html)
            for j in getids(html):
                f.write(j+',')
            print(str(i+1)+"/"+str(pages))
    
   
           

prefix = "http://agence-prd.ansm.sante.fr/php/ecodex/extrait.php?specid="

#for front page
def info_front(html):
    print(html)
    
def info_RCP(html):
    pass
    
def info_Notice(html):
    pass
    
class france_tack(base_task):
    def __init__(self,id,*args,**kw):
        self.id = id
        super(france_tack,self).__init__(*args,**kw)
        
    def run(self):
        html = get_response(prefix+self.id)
        return deal_info(html)
        
def sleep_time():
    return random.randint(2,5)
        
if __name__ == '__main__':
    #TEST
    #html = ''
    #with open('page_model.html','r') as f:
        #html = f.read()
    #deal_info(html)

    get_drugs_and_save()
    #ws = workshop(1,sleep_time)
    #with open(sava_path,'r') as f:
    #    idlist = json.loads(f.read())
    #    for i in idlist:
    #        ws.add_task(france_task(i,ws),0)
    #        
    #ws.run()

        
        
        
        
        
        
