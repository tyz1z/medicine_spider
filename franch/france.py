import requests
import random
from httputil import get_response,return_soup,post_response
import json
import re
from time import sleep
from engine import workshop,base_task,workshopRuntimeException
from mongoLink import connection,get_collection,info_model


list_url = "http://agence-prd.ansm.sante.fr/php/ecodex/index.php#result"
origin_data ={"page":1,"cherche":1,"subsid":"","nomsubs":"","affliste":0,"listeOpen":0,"lstRecherche":"denomination","radLibelle":2,"txtCaracteres":"","txtDateDebut":"","txtDateFin":"","lstEtat":0,"lstComm":0,"lstDoc":0}

html = post_response(list_url,origin_data)
soup = return_soup(html)

sava_path = "list.json"

def getids(html):
    return re.findall(r".*specid=(.*?)'>",html)

#get full list of drugs
def get_drugs_and_save():
    first_html = post_response(list_url,origin_data)
    pages = re.findall(r"</b>(.*?/.*?)</td>",first_html)[0][4:]
    pages = int(pages)
    with open(sava_path,'a') as f:
        for i in range(pages):
            origin_data['page'] = i+1
            html = post_response(list_url,origin_data)
            for j in getids(html):
                f.write(j+',')
            print(str(i+1)+"/"+str(pages))

prefix = "http://agence-prd.ansm.sante.fr/php/ecodex/extrait.php?specid="
main_prefix = "http://agence-prd.ansm.sante.fr/php/ecodex/"
    
def clear(html):
    return html.replace('\n','').replace('\r','').replace('\t','')

coll = get_collection(connection(),'france','info')
    
front_data = {
    "cis":"CIS",
    "titulaire":"Titulaire(s) de l'autorisation",
    "depuis":"Depuis le",
    "date":"Date de l'autorisation",
    "statut":"Statut de l'autorisation",
    "type":"le type de la procédure d'autorisation",
    "conditions":"Conditions de prescription et de délivrance",
    "rcp":"RCP",
    "notice":"Notice"
    }

mod = info_model(coll,front_data)
    
def deal_rcp(html):
    pass
    
def deal_notice(html):
    pass
    
#for front page
def info_front(html,id):
    html = clear(html)
    #print(html)
    data = {}
    data['cis'] = id
    
    try:
        p2 = re.findall(r'Titulaire.*? de.*?<TD colspan="4">(.*?)</TD>',html)[0]
        data['titulaire'] = p2
        
        p3 = re.findall(r'Depuis le : <B>(.*?)</B>',html)[0]
        data['depuis'] = p3
        
        p4 = re.findall(r'Date de l\'autorisation :.*?<B>(.*?)</B>',html)[0]
        data['date'] = p4
        
        p5 = re.findall(r'Statut de l\'autorisation :.*?<B>(.*?)</B>',html)[0]
        data['statut'] = p5
    
        p6 = re.findall(r'Date de l\'autorisation :.*?<TD align="right"><B>(.*?)</B>',html)[0]
        data['type'] = p6
        
        p7m = re.findall(r'Conditions de prescription.*?(<TD colspan="5">.*?)</TR><TR ',html)
        p7 = ""
        if p7m != []:
            p7 = '\n'.join(re.findall(r'<TD colspan="5">(.*?)</TD>',p7m[0]))
        data['conditions'] = p7
    except Exception as e:
        raise workshopRuntimeException("resolve error:"+str(e))
    
    p89m1 = re.findall(r'Documents de r.*?</TABLE>',html)[0]
    p89m2 = re.findall(r'<TD.*?>(.*?)</TD>',p89m1)
    #print(p89m2)
    if re.findall(r'</A>',p89m2[0]) == []:
        p8link = ""
        p9link = ""
    else:
        p8link = main_prefix+re.findall(r"<A class='leftMenu' href=(.*?)>",p89m2[0])[0]
        p9link = main_prefix+re.findall(r"<A class='leftMenu' href=(.*?)>",p89m2[1])[0]
        
    
    h8,h9,p8,p9 = "","","",""
    
    if p8link != "":
        h8 = get_response(p8link)
        p8 = deal_rcp(h8)
        
    if p9link != "":
        h9 = get_response(p9link)
        p9 = deal_notice(h9)
    
    data['rcp'] = p8
    data['notice'] = p9
    
    print(data)
    #mod.get_piece(**data).save()
    return True
    
class france_task(base_task):
    def __init__(self,id,*args,**kw):
        self.id = id
        super(france_task,self).__init__(*args,**kw)
        self.cause['token'] = id
        
    def run(self):
        html = get_response(prefix+self.id)
        if not html:
            raise workshopRuntimeException("main request failed")
        return info_front(html,self.id)
        
        
def sleep_time():
    return random.randint(1,3)
        
if __name__ == '__main__':
    #get_drugs_and_save()
    #TEST
    html = ''
    #with open('front_page_model.html','r',encoding="utf-8") as f:
    #    html = f.read()
    
    html = get_response(prefix+"68586203")
    
    info_front(html,68586203)


    
    #ws = workshop(1,sleep_time)
    #with open(sava_path,'r') as f:
    #    idlist = f.read().split(',')
    #    for i in idlist:
    #        ws.add_task(france_task(i,ws),0)
            
    #ws.test(5,debug = True)

        
        
        
        
        
        
