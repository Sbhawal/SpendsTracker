import os
from tqdm import tqdm
import base64

API_NAME='gmail'
STORE_DECRYPTED_PDFS = True
API_VERSION='v1'
SCOPES=['https://mail.google.com/']
CONFIG_FOLDER = "configs"
DOWNLOAD_FOLDER = "Downloads"
OAUTH_TOKEN_FOLDER = CONFIG_FOLDER
DB_PATH = os.path.join(CONFIG_FOLDER,"email.db")
CLIENT_SECRET_FILE_PATH = os.path.join(CONFIG_FOLDER,"client_secret.json") 
LABEL_STRUCTURE_PATH = os.path.join(CONFIG_FOLDER,"LabelStructure")
LAST_SCRAPED_DAY_PATH = os.path.join(CONFIG_FOLDER,"LAST_SCRAPED_DAY.txt")
CONDITIONS_FILE_PATH = os.path.join(CONFIG_FOLDER,"conditions")
FROM = "2023/01/01"
TO = "2024/11/24"
LAST_SCRAPED_DAY = ''
CONDITIONS = []

def read_last_Scraped_date():
    if os.path.exists(LAST_SCRAPED_DAY_PATH):
        with open(LAST_SCRAPED_DAY_PATH, "r") as f:
            FROM = f.read()
        return FROM
    else:
        return None
    
def write_last_Scraped_date(LAST_SCRAPED_DAY):
    with open(LAST_SCRAPED_DAY_PATH, "w") as f:
        f.write(LAST_SCRAPED_DAY)


with open(CONDITIONS_FILE_PATH, "r") as f:
    for line in f.readlines():
        if line.startswith("#") or len(line.strip()) == 0  or line.startswith("%"):
            continue
        else:
            CONDITIONS.append(line)
