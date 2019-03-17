import india
import time
import logging

url_list = ['http://www.way2healthcare.com/way2medicine?category=IV%20Fluids','http://www.way2healthcare.com/way2medicine?&category=N.I&per_page=49','http://www.way2healthcare.com/way2medicine?&category=Topical Corticosteroids&per_page=3','http://www.way2healthcare.com/way2medicine?category=Topical%20Antihistamines/Antipruritics','http://www.way2healthcare.com/way2medicine?category=Nonsteroidal%20Anti-Inflammatory%20Drugs%20(NSAIDs)','http://www.way2healthcare.com/way2medicine?&category=Antispasmodics&per_page=2','http://www.way2healthcare.com/way2medicine?category=Antihistamines%20&%20Antiallergics','http://www.way2healthcare.com/way2medicine?&category=Antidiabetics&per_page=10','http://www.way2healthcare.com/way2medicine?&category=Cytotoxic Chemotherapy&per_page=7','http://www.way2healthcare.com/way2medicine?&category=Antipsychotics&per_page=2','http://www.way2healthcare.com/way2medicine?&category=Antiasthmatic&per_page=7','http://www.way2healthcare.com/way2medicine?&category=Anti Anxiety&per_page=2','http://www.way2healthcare.com/way2medicine?&category=Antacids&per_page=6','http://www.way2healthcare.com/way2medicine?&category=Analgesics (Opioid)&per_page=4','http://www.way2healthcare.com/way2medicine?&per_page=36','http://www.way2healthcare.com/way2medicine?&category=Analgesic&per_page=3','http://www.way2healthcare.com/way2medicine?&category=Antibiotics&per_page=6','http://www.way2healthcare.com/way2medicine?category=Acne%20Treatment','http://www.way2healthcare.com/way2medicine?&category=Cardiovascular&per_page=9','http://www.way2healthcare.com/way2medicine?category=Topical%20Corticosteroids','http://www.way2healthcare.com/way2medicine?&category=Supplements&per_page=3','http://www.way2healthcare.com/way2medicine?category=Vitamins%20&/or%20Minerals','http://www.way2healthcare.com/way2medicine?category=%20Antimalarials']

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# FileHandler
file_handler = logging.FileHandler('retry.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log
logger.info('Start')


for url in url_list:
    logger.info('now dealing with '+url)
    india.retry_timeout(url)
    logger.info('finished')
    #print(url)

logger.info('retry finished')

