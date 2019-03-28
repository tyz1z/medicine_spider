import requests
import random
from httputil import get_response,return_soup,post_response
import json
import re
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
rcp_prefix = "http://agence-prd.ansm.sante.fr/php/ecodex/rcp/"
notice_prefix = "http://agence-prd.ansm.sante.fr/php/ecodex/notice/"
    
    
def save_file(name,content):
    with open(name,'wb') as f:
        f.write(content)

def clear(html):
    html = re.sub(r"[\n|\r|\t]",'',html)
    html = re.sub(r"</*span.*?>","",html)
    html = re.sub(r"</*b.*?>","",html)
    html = re.sub(r"</*a.*?>","",html)
    #html = html.replace('(','\(')
    #html = html.replace(')','\)')
    return html

def re_format(pat):
    pat = pat.replace('(','\(')
    pat = pat.replace(')','\)')
    return pat
    
coll = get_collection(connection(),'france','info_debug')
    
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
        html = html.replace(i,token)
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
    
    data = {
        "DENOMINATION DU MEDICAMENT":"",
        "COMPOSITION QUALITATIVE ET QUANTITATIVE":"",
        "FORME PHARMACEUTIQUE":"",
        "DONNEES CLINIQUES":"",
        "PROPRIETES PHARMACOLOGIQUES":"",
        "DONNEES PHARMACEUTIQUES":"",
        "TITULAIRE DE L’AUTORISATION DE MISE SUR LE MARCHE":"",
        "NUMERO(S) D’AUTORISATION DE MISE SUR LE MARCHE":"",
        "DATE DE PREMIERE AUTORISATION/DE RENOUVELLEMENT DE L’AUTORISATION":"",
        "DATE DE MISE A JOUR DU TEXTE":"",
        "DOSIMETRIE":"",
        "INSTRUCTIONS POUR LA PREPARATION DES RADIOPHARMACEUTIQUES":""
        }
    
    try:
        p1 = re.findall(r'DENOMINATION DU MEDICAMENT(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
        if p1 != []:
            p1 = format_piece(p1[0])
            data["DENOMINATION DU MEDICAMENT"] = p1
            
        p2 = re.findall(r'COMPOSITION QUALITATIVE ET QUANTITATIVE(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
        if p2 != []:
            p2 = format_piece(p2[0])
            data['COMPOSITION QUALITATIVE ET QUANTITATIVE'] = p2
        
        p3 = re.findall(r'FORME PHARMACEUTIQUE(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
        if p3 != []:
            p3 = format_piece(p3[0])
            data['FORME PHARMACEUTIQUE'] = p3
        
        p4 = {}
        p4l = [ "Indications thérapeutiques{0,1}",   #excel里字段和实际匹配不一致
                "Posologie et mode d'administration",
                "Contre-indications{0,1}",
                "Mises en garde spéciales et précautions d'emploi",
                "Mises en garde spéciales et précautions particulières d'emploi",
                "Mises en garde et précautions particulières d'emploi",
                "Interactions avec d.autres médicaments et autres formes d.interactions{0,1}",
                "Grossesse et allaitement",
                "Fertilité, grossesse et allaitement",
                "Effets sur l'aptitude à conduire des véhicules et à utiliser des machines",
                "Effets indésirables",
                "Surdosage"
                ]
                
        p4l_name = [ "Indications thérapeutiques",   #excel里字段和实际匹配不一致
                "Posologie et mode d'administration",
                "Contre-indications",
                "Mises en garde spéciales et précautions d'emploi",
                "Mises en garde spéciales et précautions particulières d'emploi",
                "Mises en garde et précautions particulières d'emploi",
                "Interactions avec d'autres médicaments et autres formes d'interaction",
                "Grossesse et allaitement",
                "Fertilité, grossesse et allaitement",
                "Effets sur l'aptitude à conduire des véhicules et à utiliser des machines",
                "Effets indésirables",
                "Surdosage"
                ]
        p4pat = r'(4\.\d+(\. | ){replace})[^),]{1,2}/p>(.*?)<p class="{0,1}AmmAnnexeTitre[1|2]'
        for k,name in zip(p4l,p4l_name):
            #nextpat = r"(4\.\d+(\. | )Interactions avec d'autres médicaments et autres formes d'interactions{0,1})[^),](/a>){0,1}[^),]/p>(.*?)<p class="{0,1}AmmAnnexeTitre[1|2]"
            nextpat = p4pat.replace("{replace}",k)
            #nextpat = k
            t = re.findall(nextpat,html)
            if t != []:
                #print(t[0][0])
                v = dig_inner_layer_1(name,t[0][2])
                p4[name] = v
        if len(p4) == 9:
            data['DONNEES CLINIQUES'] = p4
        else:
            raise workshopRuntimeException("rcp_p4 resolve error")
       
        p5 = {}
        p5l = [ "Propriétés pharmacodynamiques{0,1}",
                "Propriétés pharmacocinétiques{0,1}",
                "Données de sécurité préclinique[s]{0,1}"
                ]
                
        p5l_name = [ "Propriétés pharmacodynamiques",
                "Propriétés pharmacocinétiques",
                "Données de sécurité préclinique"
                ]
        p5pat = r'(5\.\d+(\. | ){replace})[^),]{1,2}/p>(.*?)<p class="{0,1}AmmAnnexeTitre[1|2]'
        for k,name in zip(p5l,p5l_name):
            t = re.findall(p5pat.replace("{replace}",k),html)
            if t != []:
                #print(t[0][0])
                v = dig_inner_layer_1(name,t[0][2])
                p5[name] = v
            
        if len(p5) == 3:
            data['PROPRIETES PHARMACOLOGIQUES'] = p5
        else:
            raise workshopRuntimeException("rcp_p5 resolve error")
        
        p6 = {}
        p6l = [ "Liste des excipients{0,1}",
                "Incompatibilités{0,1}",
                "Durée de conservation",
                "Précautions particulières de conservation",
                "Nature et contenu de l'emballage extérieur",
                "Nature et contenance du récipient",
                "Précautions particulières d[^e]*?élimination et de manipulation",
                "Instructions pour l'utilisation et la manipulation",
                "Instructions pour l'utilisation et la manipulation, et l'élimination",
                "Instructions pour l'utilisation {0,1}, la manipulation et l'élimination",
                "Instructions pour l'utilisation et la manipulation et l'élimination",
                "Mode d'emploi, instructions concernant la manipulation"
                ]
                
        p6l_name = [ "Liste des excipients",
                "Incompatibilités",
                "Durée de conservation",
                "Précautions particulières de conservation",
                "Nature et contenu de l'emballage extérieur",
                "Nature et contenance du récipient",
                "Précautions particulières d’élimination et de manipulation",
                "Instructions pour l'utilisation et la manipuladtion",
                "Instructions pour l'utilisation et la manipulation, et l'élimination",
                "Instructions pour l'utilisation, la manipulation et l'élimination",
                "Instructions pour l'utilisation et la manipulation et l'élimination",
                "Mode d'emploi, instructions concernant la manipulation"
                ]
        p6pat = r'(6\.\d+(\. | ){replace})[^),]{1,2}/p>(.*?)<p class="{0,1}AmmAnnexeTitre[1|2]'
        for k,name in zip(p6l,p6l_name):
            #nextpat = r'(6\.\d+(\. | )Liste des excipients{0,1})[^),](/a>){0,1}[^),]{0,1}/p>(.*?)<p class="{0,1}AmmAnnexeTitre[1|2]'
            nextpat = p6pat.replace("{replace}",k)
            #print(nextpat)
            t = re.findall(nextpat,html)
            if t != []:
                #print(t[0][0])
                v = dig_inner_layer_1(name,t[0][2])
                p6[name] = v
        if len(p6) == 6:
            data['DONNEES PHARMACEUTIQUES'] = p6
        else:
            raise workshopRuntimeException("rcp_p6 resolve error")
            
        p7 = re.findall(r'TITULAIRE DE L’AUTORISATION DE MISE SUR LE MARCHE(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
        if p7 != []:
            p7 = format_piece(p7[0])
            data['TITULAIRE DE L’AUTORISATION DE MISE SUR LE MARCHE'] = p7
            
        p8 = re.findall(r'NUMERO(S) D’AUTORISATION DE MISE SUR LE MARCHE(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
        if p7 != []:
            p7 = format_piece(p8[0])
            data['NUMERO(S) D’AUTORISATION DE MISE SUR LE MARCHE'] = p8
            
        p9 = re.findall(r'DATE DE PREMIERE AUTORISATION/DE RENOUVELLEMENT DE L’AUTORISATION(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
        if p9 != []:
            p9 = format_piece(p9[0])
            data['DATE DE PREMIERE AUTORISATION/DE RENOUVELLEMENT DE L’AUTORISATION'] = p9
            
        p10 = re.findall(r'DATE DE MISE A JOUR DU TEXTE(.*?)<p class="AmmAnnexeTitre1',html)
        if p10 != []:
            p10 = format_piece(p10[0])
            data['DATE DE MISE A JOUR DU TEXTE'] = p10
        
        p11 = re.findall(r'DOSIMETRIE(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
        if p11 != []:
            p11 = format_piece(p11[0])
            data['DOSIMETRIE'] = p11
        
        p12 = re.findall(r'INSTRUCTIONS POUR LA PREPARATION DES RADIOPHARMACEUTIQUES(.*?)<p class="{0,1}AmmAnnexeTitre1',html)
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
    p0 = re.findall(r'Liste complète des substances actives et des excipients(.*?)<p class="{0,1}AmmNoticeTitre1',html)
    if p0 != []:
        data["Liste complète des substances actives et des excipients"] = dig_inner_layer_1("Liste complète des substances actives et des excipients",p0[0])
    
    p1 = re.findall(r'Dénomination du médicament(.*?)<p class="{0,1}AmmNoticeTitre1',html)[0]
    data["Dénomination du médicament"] = format_piece(p1)
    
    p2 = re.findall(r'ANSM - Mis à jour le : (.*?)<',html)
    if p2 != []:
        data["ANSM - Mis à jour le"] = p2[0]
    
    #print(html)
    
    p3 = re.findall(r'Encadré(.*?)<p class="{0,1}AmmNoticeTitre1',html)
    if p3 != []:
        data["Encadré"] = format_piece(p3[0])
    
    p4 = []
    p4pat = ['DescriptionSpecialite','Questceque','InfoNecessaires','CommentPrendre','EffetsIndesirables','Conservation','Emballage']
    p4mod = [r'Ann3b{}">(.*?)(<.*?)<p class="*?AmmAnnexeTitre1',r'Ann3b{}">(.*?)(<.*?)CARTE DE MISE EN GARDE',r'<a name="Ann3b{}.*?>(.*?)(<.*?)</div>']
    #正常结尾，警告书结尾，无警告书结尾
    for i in p4pat:
        part = re.findall(p4mod[0].format(i),html)
        if part == []:
            part = re.findall(p4mod[1].format(i),html)
            if part == []:
                part = re.findall(p4mod[2].format(i),html)
        if part != []:
            #print(part[0][0])
            p4.append(part[0])
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
    
    h8,h9,p8,p9 = "","","",""
    
    if p8link != "":
        h8 = get_response(p8link,get_bytes = True)
        save_file("./rcp/"+str(id)+".html",h8)
        #p8 = deal_rcp(h8)
        
    if p9link != "":
        h9 = get_response(p9link,get_bytes = True)
        save_file("./notice/"+str(id)+".html",h9)
        #p9 = deal_notice(h9)
    
    #data['rcp'] = p8
    #data['notice'] = p9
    
    #print(data)
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
    return 0

def main():
    ws = workshop(5,sleep_time)
    with open(sava_path,'r') as f:
        idlist = f.read().split(',')
        for i in idlist:
            ws.add_task(france_task(i,ws),0)
            
    ws.run(debug = True)
    #ws.test(5,debug = True)
    
def load_from_failed():
    ws = workshop(5,sleep_time)
    with open("debug_failed_log_bak.txt",'r') as f:
        idlist = f.read().split('\n')
        for i in idlist:
            ws.add_task(france_task(i,ws),0)
            
    ws.run(debug = True)
    
def single(i):
    html = get_response(prefix+str(i))
    info_front(html,i)
    
if __name__ == '__main__':
    #get_drugs_and_save()
    #single(60117759 )
    #load_from_failed()
    main()
    #mod.duplicate_removal(execute = False)
    

    

        
        
        
        
        
        
