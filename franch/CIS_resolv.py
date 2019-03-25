from mongoLink import connection,get_collection,info_model

c = connection()
cl = get_collection(c,"france","CIS_info")
info_map = {"cis_code":"code CIS","name":"la dénomination de la spécialité pharmaceutique","dosage_form":"la forme pharmaceutique","route":"la ou les voies d'administration","state":"le statut de l'AMM","authorisation":"le type de la procédure d'autorisation","marketing":"l'état de commercialisation","document_code":"code de document"}
mod = info_model(cl,info_map)

path = "CIS.txt"
with open(path,"r",encoding="utf-8") as f:
    t = f.readline()
    while t :
        map = {}
        for k,v in zip(info_map.keys(),t.split('\t')):
            map[k] = v
            
        mod.get_piece(**map).save()
        t = f.readline()
            