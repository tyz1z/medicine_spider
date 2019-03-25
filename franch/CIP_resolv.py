from mongoLink import connection,get_collection,info_model

c = connection()
cl = get_collection(c,"france","CIP_info")
info_map = {"cis_code":"code CIS","cip_code":"le code CIP à 7 chiffres de la présentation","pack":"le libellé de la présentation","state":"le statut administratif de la présentation","marketing":"l'état de commercialisation de la présentation tel que déclaré par le titulaire de l'AMM","date":"la date de la déclaration","cip_code_2":"code CIP à 13 chiffres de la présentation"}
mod = info_model(cl,info_map)

path = "CIS_CIP.txt"
with open(path,"r",encoding="utf-8") as f:
    t = f.readline()
    while t :
        map = {}
        for k,v in zip(info_map.keys(),t.split('\t')):
            map[k] = v.replace('\n','')
        #print(map)
        mod.get_piece(**map).save()
        t = f.readline()
            