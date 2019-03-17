import pymongo


def connection():
	ip = "120.77.241.243"
	port = "27777"
	uname = "root"
	pwd = "I0NuZMftCMewF1Fg"
	cli = pymongo.MongoClient("mongodb://%s:%s@%s:%s/" % (uname,pwd,ip,port))
	return cli

def save(name,dosage,company,packing,molecule,category,strength,mrp):
		cli = connection()

		coll = get_collection(cli, "india", "info")

		info_map = {"brand_name": "Brand Name", "dosage_form": "Dosage Form", "company_name": "Company Name",
					"packing": "Packaging", "molecule": "Molecule", "category": "Category", "strength": "Strength",
					"mrp_rs": "MRP(Rs)"}

		india_model = info_model(coll, info_map)

		p = india_model.get_piece(brand_name=name, dosage_form=dosage, company_name=company,
								  packing=packing, molecule=molecule, category=category, strength=strength,
								  mrp_rs=mrp)

		#print(p)
		p.save()
		#print('save over')

# cli = pymongo.MongoClient("mongodb://%s:%s@%s:%s/" % (uname,pwd,ip,port))
# dbs = cli.list_database_names()

def get_collection(cli,db,collection):
	return cli[db][collection]

class info_model(object):
	def __init__(self,collection,map):
		self.collection = collection
		self.map = map
				
	def get_piece(self,**kw):
		p = info_piece(self.collection,self.map)
		p.set_dict(kw)
		return p
		
class info_piece(dict):
		def __init__(self,collection,map):
			self.collection = collection
			self.map = map
			self.data = {}
			for k,_ in map.items():
				self.data[k] = ""
			
		def __setitem__(self, key, item):
			if key in self.data:
				self.data[key] = item
				
		def set_dict(self,kw):
			for k,v in kw.items():
				self.__setitem__(k,v)
				
		def __str__(self):
			str = "{"
			for k,v in self.map.items():
				str += v+":"+self.data[k]+","
			str = str[:-1] + "}"
			return str
			
		def save(self):
			#存的时候用map后面的字段
			sav_dict = {}
			for k,v in self.map.items():
				sav_dict[v] = self.data[k]
			self.collection.insert(sav_dict)






#
# cli = connection()
#
# coll = get_collection(cli,"india","info")
#
# info_map = {"brand_name":"Brand Name","dosage_form":"Dosage Form","company_name":"Company Name","packing":"Packaging","molecule":"Molecule","category":"Category","strength":"Strength","mrp_rs":"MRP(Rs)"}
#
# india_model = info_model(coll,info_map)
# p = india_model.get_piece(brand_name="test_name",dosage_form="test_dosage",company_name="test_comp",packing="test_pack",molecule="test_mole",category="test_cate",strength="test_str",mrp_rs="test_mrp")
#
#
# print(p)
# p.save()







		
				
			
