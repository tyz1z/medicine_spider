from mongoLink import connection,get_collection,info_model

c = connection()
cl = get_collection(c,"france","COMPO_info")
info_map = {"cis_code":"code CIS","design":"la désignation de l'élément pharmaceutique décrit","substance_code":"le code de la substance","substance":"la dénomination de la substance","dosage":"le dosage de la substance","ref":"la référence de ce dosage","nature":" la nature du composant (principe actif ou fraction thérapeutique) et un numéro permettant de lier","act":"substances actives et fractions thérapeutiques"}
mod = info_model(cl,info_map)

path = "COMPO.txt"
with open(path,"r",encoding="utf-8") as f:
    t = f.readline()
    while t :
        map = {}
        for k,v in zip(info_map.keys(),t.split('\t')):
            map[k] = v.replace('\n','')
        #print(map)
        mod.get_piece(**map).save()
        t = f.readline()
            