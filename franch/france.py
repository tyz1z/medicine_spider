import requests
import random
from httputil import get_response,return_soup,post_response
import json
import re
from time import sleep
from engine import workshop,base_task,workshopRuntimeException
from mongoLink import connection,get_collection,info_model
from lxml import etree


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
rcp_prefix = "http://agence-prd.ansm.sante.fr/php/ecodex/rcp/"
notice_prefix = "http://agence-prd.ansm.sante.fr/php/ecodex/notice/"
    
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

def pull_table(html):
    source = re.findall(r'<table.*?>.*?</table>',html)
    count = 0
    source_map = {}
    for i in source:
        token = "{blankFilling_%d}" % count
        html = re.sub(i,token,html)
        count += 1
        source_map[token] = i
   
    return html,source_map

def push_table(h,source_map):
    for k,v in source_map.items():
        h = h.replace(k,v)
    return h

def format_piece(html):
    h,s = pull_table(html)
    h = re.sub('(</.*?>)+','\n',h)
    h = re.sub('<.*?>','',h)
    return push_table(h,s)

def dig_inner_layer_1(title,layer1):
    #预处理
    layer1 += "<end>"
    layer1 = re.sub(r"<p class=AmmAnnexeTitre3>","<end><p class=AmmAnnexeTitre3>",layer1)
    
    data = {}
    
    l = re.findall(r"<p class=AmmAnnexeTitre3>(.*?)</p>(.*?)<end>",layer1)
    if l == []:
        return format_piece(layer1)
    else:
        #匹配上级标题与下级标题间无所属的部分
        l0 = re.search(r"(.*?)<end>",layer1).group(0)
        l0 = format_piece(l0)
        if l0 != "":
            if title == "Propriétés pharmacodynamiques":   #rcp 5.1 特殊处理
                l0_d = re.findall(r"Classe pharmacothérapeutique : (.*?), code ATC : (.{7})",l0)
                if len(l0_d) != 0:
                    #print(l0_d)
                    data["Classe pharmacothérapeutique"] = l0_d[0][0]
                    data["code ATC"] = l0_d[0][1]
            else:
                data[title] = l0

    for k,v in l:
        #print('1',k,v)
        data[k] = dig_inner_layer_2(k,v)
    return data

def dig_inner_layer_2(title,layer2):
    layer2 += "<end>"
    layer2 = re.sub(r"<p class=AmmAnnexeTitre4>","<end><p class=AmmAnnexeTitre4>",layer2)
    
    data = {}
    
    l = re.findall(r"<p class=AmmAnnexeTitre4>(.*?)</p>(.*?)<end>",layer2)
    if l == []:
        return format_piece(layer2)
    else:
        #匹配上级标题与下级标题间无所属的部分
        l0 = re.search(r"(.*?)<end>",layer2).group(0)
        l0 = format_piece(l0)
        if l0 != "":
            data[title] = l0
            #print('1',title,l0)  

    for k,v in l:
        #print(' 2',k)
        data[k] = format_piece(v)
    return data

    
def deal_rcp(html):
    html = clear(html)
    
    inner_data_1 = {
        "Indications thérapeutiques":"",
        "Posologie et mode d'administration":"",
        "Contre-indications":"",
        "Mises en garde spéciales et précautions d'emploi":"",
        "Interactions avec d'autres médicaments et autres formes d'interactions":"",
        "Fertilité, grossesse et allaitement":"",
        "Effets sur l'aptitude à conduire des véhicules et à utiliser des machines":"",
        "Effets indésirables":"",
        "Surdosage":""
        }
        
    inner_data_2 = {
        "Propriétés pharmacodynamiques":"",
        "Propriétés pharmacocinétiques":"",
        "Données de sécurité préclinique":""
        }
        
    inner_data_3 = {
        "Liste des excipients":"",
        "Incompatibilités":"",
        "Durée de conservation":"",
        "Précautions particulières de conservation":"",
        "Nature et contenu de l'emballage extérieur":"",
        "Précautions particulières d’élimination et de manipulation":""
        }
    
    data = {
        "DENOMINATION DU MEDICAMENT":"",
        "COMPOSITION QUALITATIVE ET QUANTITATIVE":"",
        "FORME PHARMACEUTIQUE":"",
        "DONNEES CLINIQUES":inner_data_1,
        "PROPRIETES PHARMACOLOGIQUES":inner_data_2,
        "DONNEES PHARMACEUTIQUES":inner_data_3,
        "TITULAIRE DE L’AUTORISATION DE MISE SUR LE MARCHE":"",
        "NUMERO(S) D’AUTORISATION DE MISE SUR LE MARCHE":"",
        "DATE DE PREMIERE AUTORISATION/DE RENOUVELLEMENT DE L’AUTORISATION":"",
        "DATE DE MISE A JOUR DU TEXTE":"",
        "DOSIMETRIE":"",
        "INSTRUCTIONS POUR LA PREPARATION DES RADIOPHARMACEUTIQUES":""
        }
    
    try:
        p1 = re.findall(r'DENOMINATION DU MEDICAMENT(.*?)<p class="AmmAnnexeTitre',html)
        if p1 != []:
            p1 = format_piece(p1[0])
            data["DENOMINATION DU MEDICAMENT"] = p1
            
        p2 = re.findall(r'COMPOSITION QUALITATIVE ET QUANTITATIVE(.*?)<p class="AmmAnnexeTitre',html)
        if p2 != []:
            p2 = format_piece(p2[0])
            data['COMPOSITION QUALITATIVE ET QUANTITATIVE'] = p2
        
        p3 = re.findall(r'FORME PHARMACEUTIQUE(.*?)<p class="AmmAnnexeTitre',html)
        if p3 != []:
            p3 = format_piece(p3[0])
            data['FORME PHARMACEUTIQUE'] = p3
        
        p4 = inner_data_1
        p4m = re.findall(r'>4\.\d+\. .*?</a></p>(.*?)<p class="AmmAnnexeTitre',html)
        if len(p4m) == 9:
            #t = dig_inner_layer_1("sth",p4m[7])
            #print(json.dumps(t))
            for k,v in zip(p4.keys(),p4m):
                t = dig_inner_layer_1(k,v)
                p4[k] = t
            data['DONNEES CLINIQUES'] = p4
        else:
            raise workshopRuntimeException("rcp_p4 resolve error")
            
        p5 = inner_data_2
        p5m = re.findall(r'>5\.\d+\. .*?</a></p>(.*?)<p class="AmmAnnexeTitre',html)
        if len(p5m) == 3:
            for k,v in zip(p5.keys(),p5m):
                t = dig_inner_layer_1(k,v)
                p5[k] = t
            data['PROPRIETES PHARMACOLOGIQUES'] = p5
        else:
            raise workshopRuntimeException("rcp_p5 resolve error")
        
        p6 = inner_data_3
        p6m = re.findall(r'>6\.\d+\. .*?</a></p>(.*?)<p class="AmmAnnexeTitre',html)
        if len(p6m) == 6:
            for k,v in zip(p6.keys(),p6m):
                t = dig_inner_layer_1(k,v)
                p6[k] = t
            data['DONNEES PHARMACEUTIQUES'] = p6
        else:
            raise workshopRuntimeException("rcp_p6 resolve error")
            
        p7 = re.findall(r'TITULAIRE DE L’AUTORISATION DE MISE SUR LE MARCHE(.*?)<p class="AmmAnnexeTitre',html)
        if p7 != []:
            p7 = format_piece(p7[0])
            data['TITULAIRE DE L’AUTORISATION DE MISE SUR LE MARCHE'] = p7
            
        p8 = re.findall(r'NUMERO(S) D’AUTORISATION DE MISE SUR LE MARCHE(.*?)<p class="AmmAnnexeTitre',html)
        if p7 != []:
            p7 = format_piece(p8[0])
            data['NUMERO(S) D’AUTORISATION DE MISE SUR LE MARCHE'] = p8
            
        p9 = re.findall(r'DATE DE PREMIERE AUTORISATION/DE RENOUVELLEMENT DE L’AUTORISATION(.*?)<p class="AmmAnnexeTitre',html)
        if p9 != []:
            p9 = format_piece(p9[0])
            data['DATE DE PREMIERE AUTORISATION/DE RENOUVELLEMENT DE L’AUTORISATION'] = p9
            
        p10 = re.findall(r'DATE DE MISE A JOUR DU TEXTE(.*?)<p class="AmmAnnexeTitre',html)
        if p10 != []:
            p10 = format_piece(p10[0])
            data['DATE DE MISE A JOUR DU TEXTE'] = p10
        
        p11 = re.findall(r'DOSIMETRIE(.*?)<p class="AmmAnnexeTitre',html)
        if p11 != []:
            p11 = format_piece(p11[0])
            data['DOSIMETRIE'] = p11
        
        p12 = re.findall(r'INSTRUCTIONS POUR LA PREPARATION DES RADIOPHARMACEUTIQUES(.*?)<p class="AmmAnnexeTitre',html)
        if p12 != []:
            p12 = format_piece(p12[0])
            data['INSTRUCTIONS POUR LA PREPARATION DES RADIOPHARMACEUTIQUES'] = p12
            
        #print(json.dumps(data))
        return json.dumps(data)
        
    except workshopRuntimeException as e:
        raise e
    except Exception as e:
        raise workshopRuntimeException("rsp resolve error:"+str(e))
      
    return False
    
    
def deal_notice(html):
    html = clear(html)
    
    data = {
        "Dénomination du médicament":"",
        "ANSM - Mis à jour le":"",
        "Encadré":"",
        "CARTE DE MISE EN GARDE":""
        }
    
    p1 = re.findall(r'Dénomination du médicament(.*?)<p class="AmmNoticeTitre',html)[0]
    p1 = format_piece(p1)
    #print(p1)
    
    p2 = re.findall(r'ANSM - Mis à jour le : (.*?)<',html)[0]
    #print(p2)
    
    p3 = re.findall(r'Encadré(.*?)<p class="AmmNoticeTitre',html)[0]
    p3 = format_piece(p3)
    #print(p3)
    
    p4 = []
    p4 += re.findall(r'Ann3bQuestceque">(.*?)(<.*?)<p class="AmmAnnexeTitre1',html)
    p4 += re.findall(r'Ann3bInfoNecessaires">(.*?)(<.*?)<p class="AmmAnnexeTitre1',html)
    p4 += re.findall(r'Ann3bCommentPrendre">(.*?)(<.*?)<p class="AmmAnnexeTitre1',html)
    p4 += re.findall(r'Ann3bEffetsIndesirables">(.*?)(<.*?)<p class="AmmAnnexeTitre1',html)
    p4 += re.findall(r'Ann3bConservation">(.*?)(<.*?)<p class="AmmAnnexeTitre1',html)
    p4 += re.findall(r'Ann3bEmballage">(.*?)(<.*?)CARTE DE MISE EN GARDE',html) #以警告书结尾的
    if len(p4) != 6:
        p4 += re.findall(r'<a name="Ann3bEmba.*?>(.*?)(<.*?)</div>',html)       #没有警告书的
    for k,v in p4:
        data[k] = dig_inner_layer_1(k,v)
    
    p5m = re.findall(r'CARTE DE MISE EN GARDE(.*?)</p>(.*)',html)
    if p5m != []:
        p5 = {"CARTE DE MISE EN GARDE":p5m[0][0]}
        p5m2 = re.findall(r'CE \d+(.*?)FA',p5m[0][1])
        c = 1
        for i in p5m2:
            p5["FACE %d" % c] = format_piece(i)
            #print(format_piece(i))
            c += 1
        data["CARTE DE MISE EN GARDE"] = p5
    
    return json.dumps(data)
    
#for front page
def info_front(html,id):
    html = clear(html)
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
        p8link = rcp_prefix+re.findall(r"<A class='leftMenu' href=.*(R.*?\.htm)'>",p89m2[0])[0]
        p9link = notice_prefix+re.findall(r"<A class='leftMenu' href=.*(N.*?\.htm)'>",p89m2[1])[0]
        
    #print(p8link)
    #print(p9link)
    
    h8,h9,p8,p9 = "","","",""
    
    if p8link != "":
        h8 = get_response(p8link)
        p8 = deal_rcp(h8)
        
    if p9link != "":
        h9 = get_response(p9link)
        p9 = deal_notice(h9)
    
    data['rcp'] = p8
    data['notice'] = p9
    
    #print(data)
    mod.get_piece(**data).save()
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
    html = ''
    #with open('front_page_model.html','r',encoding="utf-8") as f:
    #    html = f.read()
    test_num = 61679174
    html = get_response(prefix+"65196479")
    
    info_front(html,68586203)

    #ws = workshop(1,sleep_time)
    #with open(sava_path,'r') as f:
    #    idlist = f.read().split(',')
    #    for i in idlist:
    #        ws.add_task(france_task(i,ws),0)
            
    #ws.test(5,debug = True)

        
        
        
        
        
        
