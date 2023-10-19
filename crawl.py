import requests
import os
import shutil
import time
from lets_common_log import logUtils as log
import config
import pymysql
from time import localtime, strftime

def txtLOG_errorAdded(msg):
    # .txt로 로그 남기기
    # 파일을 추가 모드로 열고 데이터 추가하기
    log.error(msg)
    with open('crawl log.txt', 'a') as file:
        file.write(f'[{strftime("%Y-%m-%d %H:%M:%S", localtime())}] - {msg}\n\n')

start = time.time()

conf = config.config("config.ini")

host = conf.config["db"]["host"]
port = int(conf.config["db"]["port"])
username = conf.config["db"]["username"]
password = conf.config["db"]["password"]
database = conf.config["db"]["database-cheesegull"]

try:
    db = pymysql.connect(host=host, port=port, user=username, passwd=password, db=database, charset='utf8')
    cursor = db.cursor()
except:
    log.error("DB 연결 실패!")


cursor.execute(f"SELECT id FROM cheesegull.sets WHERE id >= 8016 ORDER BY id")
SetID = cursor.fetchall()

log.debug(f"len(SetID) = {len(SetID)}")

Header = {
    "User-Agent": "mediaserver self crawl"
}

""" def bg():
    for i in SetID:
        i = i[0]
        r = requests.get(f"https://b.redstar.moe/bg/+{i}", headers=Header)
        if r.status_code != 200:
            txtLOG_errorAdded(f"bsid = +{i} | status_code = {r.status_code}")

        time.sleep(1) """

def thumb():
    for i in SetID:
        i = i[0]
        r = requests.get(f"https://b.redstar.moe/thumb/{i}l.jpg", headers=Header)
        if r.status_code != 200:
            txtLOG_errorAdded(f"bsid = {i}l.jpg | status_code = {r.status_code}")

        r2 = requests.get(f"https://b.redstar.moe/thumb/{i}.jpg", headers=Header)
        if r2.status_code != 200:
            txtLOG_errorAdded(f"bsid = {i}.jpg | status_code = {r2.status_code}")

        time.sleep(1)

def preview():
    for i in SetID:
        i = i[0]
        r = requests.get(f"https://b.redstar.moe/preview/{i}.mp3", headers=Header)
        if r.status_code != 200:
            txtLOG_errorAdded(f"bsid = {i}.mp3 | status_code = {r.status_code}")

        time.sleep(1)

thumb()

log.info("thumb 완료!!!")
middle = time.time()
log.chat(f"{middle - start} Sec")

preview()

end = time.time()
log.chat(f"{end - start} Sec")