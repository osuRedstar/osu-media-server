from helpers import config
import threading
import requests
import tarfile
import os
from datetime import datetime
import time
from helpers import logUtils as log

conf = config.config("config.ini")
mmdbID = conf.config["mmdb"]["id"]
mmdbKey = conf.config["mmdb"]["key"]

def mmdbdl():
    r = requests.get("https://download.maxmind.com/geoip/databases/GeoLite2-City/download?suffix=tar.gz", auth=(mmdbID, mmdbKey)).content
    with open("mmdb.tar.gz", "wb") as f: f.write(r)
    with tarfile.open("mmdb.tar.gz", 'r:gz') as tar: tar.extractall("mmdb")

    mmdbDir = os.listdir('mmdb')[0]
    mmdbFile = [file for file in os.listdir(f"mmdb/{mmdbDir}") if file.endswith(".mmdb")][0]
    os.replace(f"mmdb/{mmdbDir}/{mmdbFile}", "GeoLite2-City.mmdb")
    os.system("rd /s /q mmdb && del /f /q mmdb.tar.gz")

def wk():
    while True:
        now = datetime.now(); print(now)
        if now.weekday() == 0 and now.hour == 0: mmdbdl()
        time.sleep(1800)

def dl():
    if not os.path.isfile("GeoLite2-City.mmdb"): mmdbdl(); log.warning("GeoLite2-City.mmdb 없어서 다운로드함")
    thread = threading.Thread(target=wk)
    thread.start()