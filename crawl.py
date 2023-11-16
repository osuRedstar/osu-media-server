import requests
import os
import shutil
import time
from lets_common_log import logUtils as log
import config
import pymysql
from time import localtime, strftime
from dbConnent import db

def txtLOG_errorAdded(msg):
    # .txt로 로그 남기기
    # 파일을 추가 모드로 열고 데이터 추가하기
    log.error(msg)
    with open('crawl log.txt', 'a') as file:
        file.write(f'[{strftime("%Y-%m-%d %H:%M:%S", localtime())}] - {msg}\n\n')

start = time.time()

start_bsid = 209888
SetID = db("cheesegull").fetch("SELECT id FROM sets WHERE id >= %s ORDER BY id", (start_bsid))

log.debug(f"len(SetID) = {len(SetID)}")

Header = {
    "User-Agent": "mediaserver self crawl"
}

def insertDBStatusCode(bsid, r):
    sql = '''
        SELECT CONCAT(s.artist, ' - ', s.title, ' (', s.creator, ')') AS filename
        FROM sets AS s
        WHERE s.id = %s
    '''
    filename = db("cheesegull").fetch(sql, (bsid))["filename"]
    e = r.headers.get('Exception', None)
    nowTime = time.time()
    result = db("cheesegull").fetch("SELECT * FROM download_status WHERE bsid = %s", (bsid))
    if result is None:
        db("cheesegull").execute("INSERT INTO download_status (id, bsid, filename, http_statusCode, Exception, update_time) VALUE (%s, %s, %s, %s, %s, %s)", ("NULL", bsid, filename, r.status_code, e, nowTime))
    else:
        log.warning(f"cheesegull.download_status 테이블이 이미 {bsid} 비트맵셋에 대한 정보가 있음")
        db("cheesegull").execute("UPDATE download_status SET http_statusCode = %s, Exception = %s, update_time = %s WHERE bsid = %s", (r.status_code, e, nowTime, bsid))

host = "http://localhost:6199"

""" def bg():
    for i in SetID:
        i = i["id"]
        r = requests.get(f"{host}/bg/+{i}", headers=Header)
        if r.status_code != 200:
            txtLOG_errorAdded(f"bsid = +{i} | status_code = {r.status_code}")

        insertDBStatusCode(i, r)

        time.sleep(5) """

def thumb():
    for i in SetID:
        thumbLock = False
        i = i["id"]
        r = requests.get(f"{host}/thumb/{i}l.jpg", headers=Header)
        if r.status_code != 200:
            txtLOG_errorAdded(f"bsid = {i}l.jpg | status_code = {r.status_code}")
            thumbLock = True

        if not thumbLock:
            r2 = requests.get(f"{host}/thumb/{i}.jpg", headers=Header)
            if r2.status_code != 200:
                txtLOG_errorAdded(f"bsid = {i}.jpg | status_code = {r2.status_code}")
        else:
            log.warning(f"{i} | 코드 {r.status_code}으로 thumb 1번만 요청함")
        
        insertDBStatusCode(i, r)

        time.sleep(5)

def preview():
    for i in SetID:
        i = i["id"]
        r = requests.get(f"{host}/preview/{i}.mp3", headers=Header)
        if r.status_code != 200:
            txtLOG_errorAdded(f"bsid = {i}.mp3 | status_code = {r.status_code}")

        insertDBStatusCode(i, r)

        time.sleep(5)

thumb()

log.info("thumb 완료!!!")
middle = time.time()
log.chat(f"{middle - start} Sec")

preview()

end = time.time()
log.chat(f"{end - start} Sec")