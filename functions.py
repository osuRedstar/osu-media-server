from helpers import logUtils as log
#from helpers.dbConnect import db
from helpers import dbConnector
import zipfile
import os
import shutil
import requests
from tqdm import tqdm
from helpers import config
from PIL import Image
import hashlib
import re
from pydub.utils import mediainfo
import threading
import time
from datetime import datetime
import json
from collections import Counter
import geoip2.database
from helpers import mods
import traceback

def exceptionE(msg=""): e = traceback.format_exc(); log.error(f"{msg} \n{e}"); return e

class calculate_md5:
    @classmethod
    def file(cls, fn) -> str:
        if os.path.getsize(fn) > 1073741824: return None
        md5 = hashlib.md5()
        with open(fn, "rb") as f: md5.update(f.read())
        return md5.hexdigest()

    @classmethod
    def text(cls, t) -> str:
        md5 = hashlib.md5()
        md5.update(t.encode("utf-8"))
        return md5.hexdigest()

conf = config.config("config.ini")
isLog = eval(conf.config["server"]["isLog"])
OSU_APIKEYS = eval(conf.config["osu"]["Bancho_Apikeys"])
Bancho_u = conf.config["osu"]["Bancho_username"]
Bancho_p = conf.config["osu"]["Bancho_password"]
Bancho_p_hashed = calculate_md5.text(Bancho_p)
#lets.py 형태의 사설서버를 소유중이면 lets\.data\beatmaps 에서만 .osu 파일을 가져옴
IS_YOU_HAVE_OSU_PRIVATE_SERVER = eval(conf.config["osu"]["IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py"])
lets_beatmaps_Folder = conf.config["osu"]["lets.py_beatmaps_Folder_Path"]
dataFolder = conf.config["server"]["dataFolder"]
oszRenewTime = int(conf.config["server"]["oszRenewTime"])
osuServerDomain = conf.config["server"]["osuServerDomain"]

dbR = dbConnector.db(conf.config["db"]["database"])
dbC = dbConnector.db("cheesegull")
dbO = dbConnector.db("osu_media_server")

mmdbID = conf.config["mmdb"]["id"]
mmdbKey = conf.config["mmdb"]["key"]

requestHeaders = {"User-Agent": f"RedstarOSU's MediaServer (python requests) | https://b.{osuServerDomain}"}
OSisWindows = os.name == "nt"

def BanchoApiRequest(url: str, params: dict, apsc: bool=False):
    """
    url: str - https://osu.ppy.sh 를 제외한 url을 입력하세요
                Enter any URL except https://osu.ppy.sh
    params: dict - apikey 파라미터인 "k" 는 생략해도 됩니다. (어짜피 함수 내부에서 수정됩니다.)
                    The apikey parameter, “k”, can be omitted. (it will be modified inside the function anyway.)
    """
    rt = []; url = f"https://osu.ppy.sh{url}"
    for i, k in enumerate(OSU_APIKEYS):
        params["k"] = k
        if apsc: rt.append(requests.get(url, params=params, headers=requestHeaders).status_code)
        else:
            rq = requests.get(url, params=params, headers=requestHeaders)
            if rq.status_code != 200: log.warning(f"apikey {i + 1} | status_code = {rq.status_code}"); continue
            else: rt = rq; break
    return rt

log.info("Bancho apikeyStatus check...") #API 키 테스트
apikeyStatus = False
for i, sc in enumerate(BanchoApiRequest("/api/get_beatmaps", params={'b': -1}, apsc=True)):
    if sc != 200:
        log.warning(f"[!] Bancho apikey {i + 1} does not work.")
        log.warning("[!] Please edit your config.ini and run the server again.")
    else: log.info(f"apikey {i + 1} Done!"); apikeyStatus = True
if not apikeyStatus: exit(); del apikeyStatus

#ffmpeg 설치확인
if os.system(f"ffmpeg -version > {'nul' if OSisWindows else '/dev/null'} 2>&1") != 0:
    log.warning(f"ffmpeg Does Not Found!! | ignore? (y/n) ")
    if input("").lower() != "y":
        print("exit")
        if OSisWindows: print("https://github.com/BtbN/FFmpeg-Builds/releases")
        else: print("sudo apt install ffmpeg")
        exit()
    else:
        print("ignored")
        log.warning("Maybe Not work preview & audio (DT, NC, HT)")

####################################################################################################

# main.py
ContectEmail = conf.config["server"]["ContectEmail"]
allowedconnentedbot = eval(conf.config["server"]["allowedconnentedbot"])
if allowedconnentedbot: log.chat("봇 접근 허용")
else: log.warning("봇 접근 거부")

def findBot(ip=None, country=None, url=None, user_agent=None, referer=None, botType=None, count=None, last_seen=None):
    sql = "SELECT * FROM ips WHERE TRUE"; params = []
    if ip: sql += " AND IP LIKE %s"; params.append(f"%{ip}%")
    if country: sql += " AND Country LIKE %s"; params.append(f"%{country}%")
    if url: sql += " AND URL LIKE %s"; params.append(f"%{url}%")
    if user_agent: sql += " AND User_Agent LIKE %s"; params.append(f"%{user_agent}%")
    if referer: sql += " AND Referer LIKE %s"; params.append(f"%{referer}%")
    if botType: sql += " AND Type LIKE %s"; params.append(f"%{botType}%")
    if count is not None: sql += " AND Count = %s"; params.append(int(count))
    if last_seen is not None: sql += " AND Last_seen = %s"; params.append(int(last_seen))
    sql += " ORDER BY id"
    return dbO.fetchAll(sql, params)

def getIP(self):
    if "X-Real-IP" in self.request.headers: return self.request.headers.get("X-Real-IP") #Added from nginx
    elif "CF-Connecting-IP" in self.request.headers: return self.request.headers.get("CF-Connecting-IP")
    elif "X-Forwarded-For" in self.request.headers: return self.request.headers.get("X-Forwarded-For")
    else: return self.request.remote_ip

def IPtoFullData(IP): #전체 정보를 가져오기 위한 코드
    reader = geoip2.database.Reader("GeoLite2-City.mmdb")
    try:
        res = reader.city(IP)
        data = {
            "ip": IP,
            "city": res.city.name,
            "region": res.subdivisions.most_specific.name,
            "country": res.country.iso_code,
            "country_full": res.country.name,
            "continent": res.continent.code,
            "continent_full": res.continent.name,
            "loc": f"{res.location.latitude},{res.location.longitude}",
            "postal": res.postal.code if res.postal.code else ""
        }
    except geoip2.errors.AddressNotFoundError:
        data = {
            "ip": IP, "city": "Unknown", "region": "Unknown", "country": "XX", "country_full": "Unknown", "continent": "Unknown", "continent_full": "Unknown", "loc": "Unknown", "postal": "Unknown"
        }
        log.error(f"주어진 IP 주소 : {IP} 를 찾을 수 없습니다.")
    except:
        data = {
            "ip": IP, "city": "Unknown", "region": "Unknown", "country": "XX", "country_full": "Unknown", "continent": "Unknown", "continent_full": "Unknown", "loc": "Unknown", "postal": "Unknown"
        }
        exceptionE("국가코드 오류 발생")
    finally: reader.close()
    return data

def getRequestInfo(self):
    IsCloudflare = IsNginx = IsHttp = False
    real_ip = getIP(self)
    try:
        request_url = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
        country_code = self.request.headers["Cf-Ipcountry"]
        IsCloudflare = IsNginx = True
        Server = "Cloudflare"
    except Exception as e:
        log.warning(f"cloudflare를 거치지 않음, real_ip는 nginx header에서 가져옴 | e = {e}")
        try:
            request_url = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
            IsNginx = True
            if OSisWindows:
                try: Server = os.popen("nginx.exe -v 2>&1").read().split(":")[1].strip()
                except: ngp = os.getcwd().replace(os.getcwd().split("\\")[-1], "nginx/nginx.exe").replace("\\", "/"); Server = os.popen(f'{ngp} -v 2>&1').read().split(":")[1].strip()
            else: Server = os.popen("nginx -v 2>&1").read().split(":")[1].strip()
        except Exception as e:
            log.warning(f"http로 접속시도함 | cloudflare를 거치지 않음, real_ip는 http 요청이라서 바로 뜸 | e = {e}")
            request_url = self.request.protocol + "://" + self.request.host + self.request.uri
            IsHttp = True
            Server = self._headers.get("Server")
        country_code = IPtoFullData(real_ip)["country"]
    client_ip = self.request.remote_ip
    try: User_Agent = self.request.headers["User-Agent"]
    except: User_Agent = ""; log.error("User-Agent 값이 존재하지 않음!")
    try: Referer = self.request.headers["Referer"]; log.info("Referer 값이 존재함!")
    except: Referer = ""
    return real_ip, request_url, country_code, client_ip, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server

def request_msg(self, botpass=False):
    # Logging the request IP address
    print("")
    
    real_ip, request_url, country_code, client_ip, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server = getRequestInfo(self)

    rMsg = f"Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}"
    rt = 200
    def logmsg(rtc, msg):
        nonlocal rMsg, rt; rMsg, rt = (msg, rtc)
        if botpass: log.warning(msg)
        else: log.error(msg)

    #필?터?링
    if allowedconnentedbot: userType = "user"; blocked = 0; log.info(rMsg)
    else:
        with open("botList.json", "r") as f:
            botList = json.load(f)
            if any(i.lower() in User_Agent.lower() for i in botList["no"]) and not any(i in User_Agent.lower() for i in botList["ok"]):
                userType = "bot"; blocked = 1; logmsg(userType, f"{userType} 감지! | {rMsg}")
            elif "python-requests".lower() in User_Agent.lower():
                userType = "python-requests"; blocked = 1; logmsg(userType, f"{userType} 감지! | {rMsg}")
            elif "Python-urllib".lower() in User_Agent.lower():
                userType = "Python-urllib"; blocked = 1; logmsg(userType, f"{userType} 감지! | {rMsg}")

            elif any(i.lower() in User_Agent.lower() for i in botList["ok"]):
                userType = "okbot"; blocked = 0; rMsg = f"bot 감지! | {rMsg}"; log.info(rMsg)
            elif "PostmanRuntime".lower() in User_Agent.lower():
                userType = "PostmanRuntime"; blocked = 0; rMsg = f"{userType} 감지! | {rMsg}"; log.debug(rMsg)
            elif User_Agent == "osu!":
                userType = "osu!"; blocked = 0; rMsg = f"{userType} 감지! | {rMsg}"; log.info(rMsg)
            else:
                userType = "user"; blocked = 0; log.info(rMsg)
    #IP DB 로깅
    ips = dbO.fetchAll("SELECT * FROM ips WHERE IP = %s ORDER BY Last_seen DESC", [real_ip])
    cnt = dbO.fetch("SELECT COALESCE(SUM(Count), 0) AS cnt FROM ips WHERE IP = %s", [real_ip])["cnt"]
    nt = int(time.time())
    if ips and len(ips) > 1:
        for i in ips: dbO.execute("DELETE FROM ips WHERE id = %s", [i["id"]])
        ips = None
    if ips:
        sql = "UPDATE ips SET Country = %s, URL = %s, `User-Agent` = %s, Referer = %s, Type = %s, Count = %s, Last_seen = %s, blocked = %s WHERE id = %s"
        dbO.execute(sql, [country_code, request_url, User_Agent, Referer, userType, ips[0]["Count"] + 1, nt, blocked, ips[0]["id"]])
    else: dbO.execute("INSERT INTO ips VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [None, real_ip, country_code, request_url, User_Agent, Referer, userType, cnt + 1, nt, blocked])
    return rt

def resPingMs(self):
    pingMs = (time.time() - self.request._start_time) * 1000
    log.chat(f"{pingMs} ms")
    return pingMs

def send401(self, errMsg: str):
    self.set_status(401)
    self.set_header("Content-Type", "application/json")
    self.write(json.dumps({"code": 401, "error": errMsg}, indent=2, ensure_ascii=False))
    self.set_header("Ping", str(resPingMs(self)))

def send403(self, rm):
    self.set_status(403)
    self.set_header("Content-Type", "application/json")
    self.write(json.dumps({"code": 403, "error": f"{rm} is Not allowed!!", "message": f"contect --> {ContectEmail}"}, indent=2, ensure_ascii=False))
    self.set_header("Ping", str(resPingMs(self)))

def send404(self, inputType: str, input: str):
    self.set_status(404); self.set_header("Content-Type", "text/html")
    self.set_header("return-fileinfo", json.dumps({"filename": "404.html", "path": "templates/404.html", "fileMd5": calculate_md5.file("templates/404.html")}))
    self.render("templates/404.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

def send429(self, ttl: int):
    self.set_status(429); self.set_header("Content-Type", "text/html")
    self.render("templates/429.html", ttl=ttl)
    self.set_header("Ping", str(resPingMs(self)))

def send500(self, inputType: str, input: str):
    self.set_status(500); self.set_header("Content-Type", "text/html")
    self.set_header("return-fileinfo", json.dumps({"filename": "500.html", "path": "templates/500.html", "fileMd5": calculate_md5.file("templates/500.html")}))
    self.render("templates/500.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

def send503(self, e, inputType: str, input: str):
    self.set_status(503); self.set_header("Content-Type", "text/html")
    #Exception = json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False)
    self.set_header("Exception", json.dumps({"type": str(type(e)), "error": str(e)}))
    self.set_header("return-fileinfo", json.dumps({"filename": "503.html", "path": "templates/503.html", "fileMd5": calculate_md5.file("templates/503.html")}))
    self.render("templates/503.html", inputType=inputType, input=input, Exception=json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False))
    self.set_header("Ping", str(resPingMs(self)))

def send504(self, inputType: str, input: str):
    #cloudflare 504 페이지로 연결됨
    self.set_status(504); self.set_header("Content-Type", "text/html")
    self.set_header("return-fileinfo", json.dumps({"filename": "504.html", "path": "templates/504.html", "fileMd5": calculate_md5.file("templates/504.html")}))
    self.render("templates/504.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

IDMConnects = {}
def IDM(self, path):
    IP = getIP(self)
    filename = path.split("/")[-1]
    self.set_header("return-fileinfo", json.dumps({"filename": filename, "path": path, "fileMd5": calculate_md5.file(path)}))
    self.set_header('Content-Type', pathToContentType(path)["Content-Type"])
    self.set_header('Content-Disposition', f'inline; filename="{filename}"')
    self.set_header("Accept-Ranges", "bytes")
    if "Range" in self.request.headers:
        IDMConnects[IP] = 1 if not IDMConnects.get(IP) else IDMConnects[IP] + 1
        log.debug(f"IDMConnects[{IP}] = {IDMConnects[IP]} | {type(IDMConnects[IP])}")
        if IDMConnects[IP] > 16: send429(self, -1); return False
        idm = True
        log.info("분할 다운로드 활성화!")
        Range = self.request.headers["Range"].replace("bytes=", "").split("-")
        fileSize = os.path.getsize(path)
        start = int(Range[0])
        end = fileSize - 1 if not Range[1] else int(Range[1])
        contentLength = end - start + 1

        log.info({"Content-Range": f"bytes {start}-{end}/{fileSize}", "Content-Length": contentLength})
        self.set_status(206) if start != 0 or (start == 0 and Range[1]) else self.set_status(200)
        self.set_header("Content-Length", contentLength)
        self.set_header("Content-Range", f"bytes {start}-{end}/{fileSize}")
        with open(path, "rb") as f:
            f.seek(start); self.write(f.read(contentLength) if start != 0 or (start == 0 and Range[1]) else f.read())
        if IDMConnects[IP] > 1: IDMConnects[IP] -= 1
        else: del IDMConnects[IP]
    else:
        idm = False
        with open(path, 'rb') as f: self.write(f.read())
    return idm

def pathToContentType(path, isInclude=False):
    if path == 0: return None
    fn, fe = os.path.splitext(os.path.basename(path));
    ffln = path.replace(f"/{path.split('/')[-1]}", "")
    fln = os.path.splitext(os.path.basename(ffln.split('/')[-1]))[0]
    if OSisWindows:
        while fln.endswith("."): fln = fln[:-1]

    if isInclude and ".aac" in path.lower() or not isInclude and path.lower().endswith(".aac"): ct, tp = ("audio/aac", "audio")
    elif isInclude and ".apng" in path.lower() or not isInclude and path.lower().endswith(".apng"): ct, tp = ("image/apng", "image")
    elif isInclude and ".avif" in path.lower() or not isInclude and path.lower().endswith(".avif"): ct, tp = ("image/avif", "image")
    elif isInclude and ".avi" in path.lower() or not isInclude and path.lower().endswith(".avi"): ct, tp = ("video/x-msvideo", "video")
    elif isInclude and ".bin" in path.lower() or not isInclude and path.lower().endswith(".bin"): ct, tp = ("application/octet-stream", "file")
    elif isInclude and ".css" in path.lower() or not isInclude and path.lower().endswith(".css"): ct, tp = ("text/css", "file")
    elif isInclude and ".gif" in path.lower() or not isInclude and path.lower().endswith(".gif"): ct, tp = ("image/gif", "image")
    elif isInclude and ".html" in path.lower() or not isInclude and path.lower().endswith(".html"): ct, tp = ("text/html", "file")
    elif isInclude and ".ico" in path.lower() or not isInclude and path.lower().endswith(".ico"): ct, tp = ("image/x-icon", "image")
    elif isInclude and ".jfif" in path.lower() or not isInclude and path.lower().endswith(".jfif"): ct, tp = ("image/jpeg", "image")
    elif isInclude and ".jpeg" in path.lower() or not isInclude and path.lower().endswith(".jpeg"): ct, tp = ("image/jpeg", "image")
    elif isInclude and ".jpg" in path.lower() or not isInclude and path.lower().endswith(".jpg"): ct, tp = ("image/jpeg", "image")
    elif isInclude and ".js" in path.lower() or not isInclude and path.lower().endswith(".js"): ct, tp = ("text/javascript", "file")
    elif isInclude and ".json" in path.lower() or not isInclude and path.lower().endswith(".json"): ct, tp = ("application/json", "file")
    elif isInclude and ".mp3" in path.lower() or not isInclude and path.lower().endswith(".mp3"): ct, tp = ("audio/mpeg", "audio")
    elif isInclude and ".mp4" in path.lower() or not isInclude and path.lower().endswith(".mp4"): ct, tp = ("video/mp4", "video")
    elif isInclude and ".mpeg" in path.lower() or not isInclude and path.lower().endswith(".mpeg"): ct, tp = ("audio/mpeg", "audio")
    elif isInclude and ".oga" in path.lower() or not isInclude and path.lower().endswith(".oga"): ct, tp = ("audio/ogg", "audio")
    elif isInclude and ".ogg" in path.lower() or not isInclude and path.lower().endswith(".ogg"): ct, tp = ("application/ogg", "audio")
    elif isInclude and ".ogv" in path.lower() or not isInclude and path.lower().endswith(".ogv"): ct, tp = ("video/ogg", "video")
    elif isInclude and ".ogx" in path.lower() or not isInclude and path.lower().endswith(".ogx"): ct, tp = ("application/ogg", "audio")
    elif isInclude and ".opus" in path.lower() or not isInclude and path.lower().endswith(".opus"): ct, tp = ("audio/opus", "audio")
    elif isInclude and ".png" in path.lower() or not isInclude and path.lower().endswith(".png"): ct, tp = ("image/png", "image")
    elif isInclude and ".svg" in path.lower() or not isInclude and path.lower().endswith(".svg"): ct, tp = ("image/svg+xml", "image")
    elif isInclude and ".tif" in path.lower() or not isInclude and path.lower().endswith(".tif"): ct, tp = ("image/tiff", "image")
    elif isInclude and ".tiff" in path.lower() or not isInclude and path.lower().endswith(".tiff"): ct, tp = ("image/tiff", "image")
    elif isInclude and ".ts" in path.lower() or not isInclude and path.lower().endswith(".ts"): ct, tp = ("video/mp2t", "video")
    elif isInclude and ".txt" in path.lower() or not isInclude and path.lower().endswith(".txt"): ct, tp = ("text/plain", "file")
    elif isInclude and ".wav" in path.lower() or not isInclude and path.lower().endswith(".wav"): ct, tp = ("audio/wav", "audio")
    elif isInclude and ".weba" in path.lower() or not isInclude and path.lower().endswith(".weba"): ct, tp = ("audio/webm", "audio")
    elif isInclude and ".webm" in path.lower() or not isInclude and path.lower().endswith(".webm"): ct, tp = ("video/webm", "video")
    elif isInclude and ".webp" in path.lower() or not isInclude and path.lower().endswith(".webp"): ct, tp = ("image/webp", "image")
    elif isInclude and ".zip" in path.lower() or not isInclude and path.lower().endswith(".zip"): ct, tp = ("application/zip", "file")
    elif isInclude and ".flv" in path.lower() or not isInclude and path.lower().endswith(".flv"): ct, tp = ("video/x-flv", "video")
    elif isInclude and ".wmv" in path.lower() or not isInclude and path.lower().endswith(".wmv"): ct, tp = ("video/x-ms-wmv", "video")
    elif isInclude and ".mkv" in path.lower() or not isInclude and path.lower().endswith(".mkv"): ct, tp = ("video/x-matroska", "video")
    elif isInclude and ".mov" in path.lower() or not isInclude and path.lower().endswith(".mov"): ct, tp = ("video/quicktime", "video")

    elif isInclude and ".osz" in path.lower() or not isInclude and path.lower().endswith(".osz"): ct, tp = ("application/x-osu-beatmap-archive", "file")
    elif isInclude and ".osr" in path.lower() or not isInclude and path.lower().endswith(".osr"): ct, tp = ("application/x-osu-replay", "file")
    elif isInclude and ".osu" in path.lower() or not isInclude and path.lower().endswith(".osu"): ct, tp = ("application/x-osu-beatmap", "file")
    elif isInclude and ".osb" in path.lower() or not isInclude and path.lower().endswith(".osb"): ct, tp = ("application/x-osu-storyboard", "file")
    elif isInclude and ".osk" in path.lower() or not isInclude and path.lower().endswith(".osk"): ct, tp = ("application/x-osu-skin", "file")

    else: ct, tp = ("application/octet-stream", "?")
    return {"Content-Type": ct, "foldername": fln, "fullFoldername": ffln, "filename": fn, "extension": fe, "fullFilename": fn + fe, "type": tp, "path": path}

####################################################################################################

def getAcc(play_mode: int, count_300: int, count_100: int, count_50: int, gekis_count: int, katus_count: int, misses_count: int) -> int:
	if play_mode == 0: #Std
		total_notes = count_300 + count_100 + count_50 + misses_count
		accuracy = (300 * count_300 + 100 * count_100 + 50 * count_50) / (300 * total_notes) * 100
	elif play_mode == 1: #Taiko
		total_notes = count_300 + count_100 + misses_count
		accuracy = (count_300 + 0.5 * count_100) / total_notes * 100
	elif play_mode == 2: #CTB
		total_notes = count_300 + count_100 + count_50 + misses_count + katus_count #+ gekis_count + katus_count
		accuracy = (count_300 + count_100 + count_50) / total_notes * 100
	elif play_mode == 3: #Mania
		total_notes = gekis_count + count_300 + katus_count + count_100 + count_50 + misses_count
		accuracy = (300 * (gekis_count + count_300) + 200 * katus_count + 100 * count_100 + 50 * count_50) / (300 * total_notes) * 100
	else: accuracy = 0 #?
	return accuracy

def readableMods(__mods: int):
    """
    :param __mods: mods bitwise number
    :return: readable mods string, eg HDDT
    """
    r = ""
    if __mods == mods.NOMOD: return ""
    if __mods & mods.NOFAIL: r += "NF"
    if __mods & mods.EASY: r += "EZ"
    if __mods & mods.TOUCHSCREEN: r += "TD"
    if __mods & mods.HIDDEN: r += "HD"
    if __mods & mods.HARDROCK: r += "HR"
    if __mods & mods.SUDDENDEATH: r += "SD"
    if __mods & mods.DOUBLETIME: r += "DT"
    if __mods & mods.RELAX: r += "RX"
    if __mods & mods.HALFTIME: r += "HT"
    if __mods & mods.NIGHTCORE: r = r.replace("DT", "NC") if "DT" in r else r + "NC" #576 = DT, NC
    if __mods & mods.FLASHLIGHT: r += "FL"
    if __mods & mods.AUTOPLAY: r += "AU(AUTO)"
    if __mods & mods.SPUNOUT: r += "SO"
    if __mods & mods.RELAX2: r += "AP"
    if __mods & mods.PERFECT: r = r.replace("SD", "PF") if "SD" in r else r + "PF" #16416 = SD, PF
    if __mods & mods.KEY4: r += "K4"
    if __mods & mods.KEY5: r += "K5"
    if __mods & mods.KEY6: r += "K6"
    if __mods & mods.KEY7: r += "K7"
    if __mods & mods.KEY8: r += "K8"
    if __mods & mods.KEYMOD: r += "KEYMOD" #?
    if __mods & mods.FADEIN: r += "FI"
    if __mods & mods.RANDOM: r += "RD"
    if __mods & mods.LASTMOD: r += "LASTMOD" #?
    if __mods & mods.KEY9: r += "K9"
    if __mods & mods.KEY10: r += "K10"
    if __mods & mods.KEY1: r += "K1"
    if __mods & mods.KEY3: r += "K3"
    if __mods & mods.KEY2: r += "K2"
    if __mods & mods.SCOREV2: r += "SV2(v2)"
    if __mods & mods.MIRROR: r += "MR"
    return r

def readableModsReverse(__mods: str):
    # Check passed mods and convert to enum
    if len(__mods.upper().replace("K10", "")) % 2: __mods = "^^"
    if "K10" in __mods: __mods = __mods.replace("K10", "") + "K10"
    modsEnum = 0
    for r in [__mods[i:i+3].upper() if __mods[i:i+3].upper() == "K10" else __mods[i:i+2].upper() for i in range(0, len(__mods) if not "K10" in __mods else len(__mods) - 1, 2)]:
        if r not in ["NO", "NF", "EZ", "TD", "HD", "HR", "SD", "DT", "HT", "NC", "FL", "SO", "PF", "RX", "AP", "K4", "K5", "K6", "K7", "K8", "FI", "RD", "K9", "K10", "K1", "K3", "K2", "v2", "MR"]:
            return "Invalid mods. Allowed mods: NO, NF, EZ, TD, HD, HR, SD, DT, HT, NC, FL, SO, PF, RX, AP, K4, K5, K6, K7, K8, FI, RD, K9, K10, K1, K3, K2, v2(SV2), MR. Do not use spaces for multiple mods."
        if r == "NO": return 0
        elif r == "NF": modsEnum += mods.NOFAIL
        elif r == "EZ": modsEnum += mods.EASY
        elif r == "TD": modsEnum += mods.TOUCHSCREEN
        elif r == "HD": modsEnum += mods.HIDDEN
        elif r == "HR": modsEnum += mods.HARDROCK
        elif r == "SD": modsEnum += mods.SUDDENDEATH
        elif r == "DT": modsEnum += mods.DOUBLETIME
        elif r == "RX": modsEnum += mods.RELAX
        elif r == "HT": modsEnum += mods.HALFTIME
        elif r == "NC": modsEnum += 576 #576 = DT, NC
        elif r == "FL": modsEnum += mods.FLASHLIGHT
        elif r == "AT": modsEnum += mods.AUTOPLAY
        elif r == "SO": modsEnum += mods.SPUNOUT
        elif r == "AP": modsEnum += mods.RELAX2
        elif r == "PF": modsEnum += 16416 #16416 = SD, PF
        elif r == "K4": modsEnum += mods.KEY4
        elif r == "K5": modsEnum += mods.KEY5
        elif r == "K6": modsEnum += mods.KEY6
        elif r == "K7": modsEnum += mods.KEY7
        elif r == "K8": modsEnum += mods.k8
        #elif r == "KEYMOD": modsEnum += mods.KEYMOD
        elif r == "FI": modsEnum += mods.FADEIN
        elif r == "RD": modsEnum += mods.RANDOM
        #elif r == "LASTMOD": modsEnum += mods.LASTMOD
        elif r == "K9": modsEnum += mods.KEY9
        elif r == "K10": modsEnum += mods.KEY10
        elif r == "K1": modsEnum += mods.KEY1
        elif r == "K3": modsEnum += mods.KEY3
        elif r == "K2": modsEnum += mods.KEY2
        elif r == "v2": modsEnum += mods.SCOREV2
        elif r == "MR": modsEnum += mods.MIRROR
    return modsEnum

def get_AudioLength(filesinfo, setID, AudioFilename):
    try:
        if filesinfo:
            def culc_length(l):
                h = "{0:02d}".format(l // 60 // 60)
                m = "{0:02d}".format(l // 60)
                s = "{0:02d}".format(l % 60)
                return f"{h}:{m}:{s}"
            AudioLength = round(float(mediainfo(f"{dataFolder}/Songs/{get_osz_fullName(setID).replace('.osz', '')}/{AudioFilename}")["duration"]), 3)
            AudioLength = [AudioLength, culc_length(round(AudioLength))]
            AudioLength_DT = AudioLength_NC = [round(AudioLength[0] / 1.5, 3), culc_length(round(AudioLength[0] / 1.5))]
            #HT = 1. (AudioLength / 0.75), 2. (AudioLength * 1.5)
            AudioLength_HT = [round(AudioLength[0] / 0.75, 3), culc_length(round(AudioLength[0] / 0.75))]
        else: raise
    except: AudioLength = AudioLength_DT = AudioLength_NC = AudioLength_HT = None
    return (AudioLength, AudioLength_DT, AudioLength_NC, AudioLength_HT)

def format_size(size):
    """ 사람이 읽기 쉬운 파일 크기 포맷 """
    i = 0; units = ["Byte", "KB", "MB", "GB", "TB"]
    while size >= 1024 and i < len(units) - 1: size /= 1024; i += 1
    return f"{round(size, 2)} {units[i]}"

def get_dir_size(path='.'):
    total = 0; stack = [path]
    while stack:
        current_path = stack.pop()
        for entry in os.scandir(current_path):
            if entry.is_file(): total += entry.stat().st_size
            elif entry.is_dir(): stack.append(entry.path)
    return format_size(total)

def windowsPath(path):
    for a in ['<','>',':','"','/','\\','|','?','*']: path = path.replace(a, "_")
    return path

def folder_check():
    if not os.path.isdir(dataFolder):
        os.mkdir(dataFolder)
        log.info(f"{dataFolder} 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/dl"):
        os.mkdir(f"{dataFolder}/dl")
        log.info(f"{dataFolder}/dl 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/dl-old"):
        os.mkdir(f"{dataFolder}/dl-old")
        log.info(f"{dataFolder}/dl-old 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/Songs"):
        os.mkdir(f"{dataFolder}/Songs")
        log.info(f"{dataFolder}/Songs 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/covers"):
        os.mkdir(f"{dataFolder}/covers")
        log.info(f"{dataFolder}/covers 폴더 생성")

def get_osz_fullName(setID):
    try: return [file for file in os.listdir(f"{dataFolder}/dl/") if file.startswith(f"{setID} ")][0]
    except: return 0

def saveDB(data):
    try:
        def queryMaker():
            ranked = dbR.fetchAll("SELECT beatmap_id, ranked, latest_update FROM beatmaps WHERE beatmapset_id = %s ORDER BY beatmap_id", [data["RedstarOSU"][0]])
            if type(ranked) is dict: ranked = [ranked]
            elif ranked is None: ranked = []
            if len(data["RedstarOSU"][2]) != len(ranked) and len(data["Bancho"]) != len(ranked):
                missing_bids = list(set(d['BeatmapID'] for d in data["RedstarOSU"][2]) - set(d['beatmap_id'] for d in ranked))
                for bid in missing_bids:
                    log.info(f"{bid} pp 요청중..."); requests.get(f"https://old.{osuServerDomain}/letsapi/v1/pp?b={bid}", headers=requestHeaders)
                ranked2 = dbR.fetchAll("SELECT beatmap_id, ranked, latest_update FROM beatmaps WHERE beatmapset_id = %s ORDER BY beatmap_id", [data["RedstarOSU"][0]])
                log.chat(ranked2)
            edata = []
            for item1 in data["RedstarOSU"][2]:
                item2 = {int(item['beatmap_id']): item for item in data["Bancho"]}.get(item1['BeatmapID'], {})
                item3 = {int(item['beatmap_id']): item for item in ranked}.get(item1['BeatmapID'], {})
                edata.append({**item1, **item2, **item3})

            querys = []
            for e in edata:
                if e["update_lock"]: log.warning(f"bid = {e['BeatmapID']} | update_lock 걸림")
                temp = [None] #id
                temp.append(e['osu_file_format_v']) #osu_file_format_v
                temp.append(data["RedstarOSU"][0]) #BeatmapSetID
                temp.append(data["RedstarOSU"][1]) #first_bid
                temp.append(e['BeatmapID']) #BeatmapID
                temp.append(e['BeatmapMD5']) #BeatmapMD5
                temp.append(get_osz_fullName(data["RedstarOSU"][0]).replace(".osz", "")) #Songs_foldername
                temp.append(e['beatmapName']) #file_name

                temp.append(e['artist']) #artist 커스텀 비트맵이면 여기서 에러뜸
                temp.append(e['artist_unicode']) #artist_unicode
                temp.append(e['title']) #title
                temp.append(e['title_unicode']) #title_unicode
                temp.append(e['creator']) #creator
                temp.append(e['creator_id']) #creator_id

                temp.append(e['Version']) #Version
                temp.append(e['AudioFilename']) #AudioFilename
                temp.append(get_AudioLength(True, data["RedstarOSU"][0], e['AudioFilename'])[0][0]) #AudioLength
                temp.append(e['PreviewTime']) #PreviewTime
                temp.append(e['BeatmapBG']) #BeatmapBG
                temp.append(e['BeatmapVideo']) #BeatmapVideo

                temp.append(e['diff_size']) #CS
                temp.append(e['diff_overall']) #OD
                temp.append(e['diff_approach']) #AR
                temp.append(e['diff_drain']) #HP
                temp.append(e['total_length']) #total_length
                temp.append(e['hit_length']) #hit_length
                temp.append(e['max_combo']) #max_combo
                temp.append(e['count_normal']) #count_normal
                temp.append(e['count_slider']) #count_slider
                temp.append(e['count_spinner']) #count_spinner
                temp.append(e['bpm']) #bpm
                temp.append(e['source']) #source
                temp.append(e['tags']) #tags
                temp.append(e['packs']) #packs

                temp.append(e['ranked']) #ranked

                temp.append(e['approved']) #approved
                temp.append(e['mode']) #mode
                temp.append(e['genre_id']) #genre_id
                temp.append(e['language_id']) #language_id
                temp.append(e['storyboard']) #storyboard
                temp.append(e['download_unavailable']) #download_unavailable
                temp.append(e['audio_unavailable']) #audio_unavailable
                temp.append(e['diff_aim']) #diff_aim
                temp.append(e['diff_speed']) #diff_speed
                temp.append(e['difficultyrating']) #difficultyrating
                temp.append(e['rating']) #rating
                temp.append(e['favourite_count']) #favourite_count
                temp.append(e['playcount']) #playcount
                temp.append(e['passcount']) #passcount
                temp.append(e['submit_date']) #submit_date
                temp.append(e['approved_date']) #approved_date
                temp.append(e['last_update']) #last_update

                temp.append(e['latest_update']) #latest_update
                temp.append(e['update_lock']) #update_lock
                temp.append(1 if data["RedstarOSU"][0] < 0 or e['BeatmapID'] < 0 else 0) #CustomMap
                temp.append(time.time()) #LastChecked

                querys.append(temp)
            return querys
        isExist = dbO.fetchAll("SELECT * from beatmapsinfo_copy WHERE BeatmapSetID = %s ORDER BY id", [data["RedstarOSU"][0]])
        querys = queryMaker()
        if isExist:
            if type(isExist) is dict: isExist = [isExist]
            for ie in isExist:
                for q in querys:
                    if ie["BeatmapMD5"] == q[5]:
                        if ie["update_lock"] or (ie["last_update"] == datetime.strptime(q[51], '%Y-%m-%d %H:%M:%S')): pass
                        else:
                            q[0] = ie["id"]
                            sql = f"""
                                UPDATE beatmapsInfo_copy
                                    SET
                                        osu_file_format_v = %s, BeatmapSetID = %s, first_bid = %s, BeatmapID = %s, BeatmapMD5 = %s,
                                        Songs_foldername = %s, file_name = %s, artist = %s, artist_unicode = %s, title = %s,
                                        title_unicode = %s, creator = %s, creator_id = %s, Version = %s, AudioFilename = %s,
                                        AudioLength = %s, PreviewTime = %s, BeatmapBG = %s, BeatmapVideo = %s, CS = %s,
                                        OD = %s, AR = %s, HP = %s, total_length = %s, hit_length = %s,
                                        max_combo = %s, count_normal = %s, count_slider = %s, count_spinner = %s, bpm = %s,
                                        source = %s, tags = %s, packs = %s, ranked = %s, approved = %s,
                                        mode = %s, genre_id = %s, language_id = %s, storyboard = %s, download_unavailable = %s,
                                        audio_unavailable = %s, diff_aim = %s, diff_speed = %s, difficultyrating = %s, rating = %s,
                                        favourite_count = %s, playcount = %s, passcount = %s, submit_date = %s, approved_date = %s,
                                        last_update = %s, latest_update = %s, update_lock = %s, CustomMap = %s, LastChecked = %s
                                    WHERE id = {q.pop(0)};
                            """
                            dbO.execute(sql, q)
                            log.info(f"{q[4]} DB 업데이트 완료!")
        else:
            for q in querys:
                try:
                    sql = """
                        INSERT INTO beatmapsInfo_copy
                            VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s
                            )
                    """
                    dbO.execute(sql, q)
                except Exception as e: log.error(f"INSERT | {e}")
    except: exceptionE("saveDB | ")

def osu_file_read(setID, rq_type, bID=None, cheesegull=False, filesinfo=False):
    fullSongName = get_osz_fullName(setID)
    ptct = pathToContentType(fullSongName)

    #/filesinfo 조회시 osz 없을때 오류 방지
    if fullSongName == 0 and rq_type == "all":
        ck = check(setID, rq_type)
        if type(ck) is int: return ck
        if type(ck) is not list: return ck
        fullSongName = get_osz_fullName(setID)
        ptct = pathToContentType(fullSongName)

    #압축파일에 문제생겼을때 재 다운로드
    try: zipfile.ZipFile(f'{dataFolder}/dl/{fullSongName}').extractall(f'{dataFolder}/Songs/{ptct["foldername"]}')
    except zipfile.BadZipFile as e:
        ck = check(setID, rq_type)
        if type(ck) is int: return ck
        if type(ck) is not list:
            return ck
        try:
            zipfile.ZipFile(f'{dataFolder}/dl/{fullSongName}').extractall(f'{dataFolder}/Songs/{ptct["foldername"]}')
        except zipfile.BadZipFile as e:
            log.error(f"압축파일 오류: {e}")
    except: exceptionE("")

    oszHash = calculate_md5.file(f"{dataFolder}/dl/{fullSongName}")
    file_list = os.listdir(f"{dataFolder}/Songs/{ptct['foldername']}")
    file_list_osu = [file for file in file_list if file.endswith(".osu")]

    underV10 = False
    beatmap_info = []

    #.osu 파일명 기준으로 이름순으로 정렬함
    gullDB = dbC.fetchAll("""
        SELECT b.id, b.file_md5, CONCAT(s.artist, ' - ', s.title, ' (', s.creator, ') [', b.diff_name, ']' '.osu') AS filename, s.artist, s.title, s.creator, b.diff_name
        FROM sets AS s
        JOIN beatmaps AS b ON s.id = b.parent_set_id
        WHERE s.id = %s ORDER BY filename
    """, [setID])

    Bancho_data = choUnavailable(setID)
    audio_unavailable, download_unavailable, storyboard = Bancho_data["pylist_unavailable"]
    Bancho = Bancho_data["Bancho_data"]
    oszUpdateCheck = Bancho[0]["last_update"] if Bancho else None

    # readline_all.py
    for beatmapName in file_list_osu:
        log.info(beatmapName)
        beatmap_md5 = calculate_md5.file(f"{dataFolder}/Songs/{ptct['foldername']}/{beatmapName}")

        sql = """
            SELECT file_name as beatmapName, BeatmapMD5, osu_file_format_v, AudioFilename,
                PreviewTime, Version, BeatmapID, BeatmapBG,
                BeatmapVideo, audio_unavailable, download_unavailable, storyboard
            FROM beatmapsinfo_copy WHERE BeatmapMD5 = %s
        """
        temp = omsDB = dbO.fetch(sql, [beatmap_md5])
        if not temp: temp = {}

        with open("exceptOszList.json", "r") as file:
            exceptOszList = json.load(file)
            exceptOszList = exceptOszList["exceptOszList"] + exceptOszList["exceptOszList2"]
            update_lock = int(setID in exceptOszList)

        if temp and False: #DB 활성화 패치 진행중으로 인한 코드 정지
            temp["AudioLength"], temp["AudioLength-DT"], temp["AudioLength-NC"], temp["AudioLength-HT"] = get_AudioLength(filesinfo, setID, temp["AudioFilename"])
            log.debug((temp, omsDB, oszUpdateCheck))
        else:
            with open(f"{dataFolder}/Songs/{ptct['foldername']}/{beatmapName}", 'r', encoding="utf-8") as f:
                line = f.read()

                line = line[line.find("osu file format v"):]
                try: osu_file_format_version = int(line.split("\n")[:4][0].replace("osu file format v", "").replace(" ", ""))
                except: osu_file_format_version = 0
                if osu_file_format_version == 0: log.error("osu file format v0")
                elif osu_file_format_version < 10:
                    underV10 = True
                    log.error(f"{setID} 비트맵셋의 어떤 비트맵은 시이이이이발 osu file format 이 10이하 ({osu_file_format_version}) 이네요? 시발련들아?")
                    #틀딱곡 BeatmapID 를 Version 쪽에 넘김

                line = line[line.find("AudioFilename:"):]
                try:
                    AudioFilename = line.split("\n")[:4][0].replace("AudioFilename:", "")
                    AudioFilename = AudioFilename.replace(" ", "", 1) if AudioFilename.startswith(" ") else AudioFilename
                except: AudioFilename = None

                line = line[line.find("PreviewTime:"):]
                try:
                    PreviewTime = line.split("\n")[:4][0].replace("PreviewTime:", "")
                    PreviewTime = int(PreviewTime.replace(" ", "", 1) if PreviewTime.startswith(" ") else PreviewTime)
                except: PreviewTime = None
                
                line = line[line.find("Version:"):]
                try:
                    Version = line.split("\n")[:4][0].replace("Version:", "")
                    Version = Version.replace(" ", "", 1) if Version.startswith(" ") else Version
                except: Version = None

                if osu_file_format_version >= 10:
                    line = line[line.find("BeatmapID:"):]
                    try:
                        BeatmapID = line.split("\n")[:4][0].replace("BeatmapID:", "")
                        BeatmapID = int(BeatmapID.replace(" ", "", 1) if BeatmapID.startswith(" ") else BeatmapID)
                    except: BeatmapID = 0
                else: BeatmapID = None
                #.osu 파일에서 실제로 존재하지 않거나, 맞지않는 bid 가 있어서 점검함
                for i in gullDB if type(gullDB) == list else [gullDB]:
                    if i["file_md5"] == beatmap_md5 and BeatmapID != i["id"]:
                        log.error(f"비트맵ID 정보 서로 일치하지 않음 | [{i['diff_name']}] | BeatmapID = {BeatmapID} <-- i['id'] = {i['id']}")
                        BeatmapID = i["id"]

                line = line[line.find("//Background and Video events"):]
                try:
                    BeatmapVideo = BeatmapBG = None
                    lineSpilted = line.split("\n")[:4]
                    for p in lineSpilted:
                        t = pathToContentType(p, isInclude=True)
                        if t["type"] == "video": BeatmapVideo = p[p.find('"') + 1 : p.find('"', p.find('"') + 1)]
                        elif t["type"] == "image": BeatmapBG = p[p.find('"') + 1 : p.find('"', p.find('"') + 1)]
                except: BeatmapBG = BeatmapVideo = None

                temp["oszHash"] = oszHash
                temp["beatmapName"] = beatmapName if beatmapName != "" else None
                temp["BeatmapMD5"] = beatmap_md5
                temp["osu_file_format_v"] = osu_file_format_version if osu_file_format_version != "" else None
                temp["AudioFilename"] = AudioFilename if AudioFilename != "" else None
                temp["PreviewTime"] = PreviewTime if PreviewTime != "" else None
                temp["Version"] = Version if Version != "" else None
                temp["BeatmapID"] = BeatmapID if BeatmapID != "" else None
                temp["BeatmapBG"] = BeatmapBG if BeatmapBG != "" else None
                temp["BeatmapVideo"] = BeatmapVideo if BeatmapVideo != "" else None
                temp["audio_unavailable"] = audio_unavailable
                temp["download_unavailable"] = download_unavailable
                temp["update_lock"] = 1 if update_lock or BeatmapID < 0 or int(setID) < 0 else 0
                temp["storyboard"] = storyboard
                temp["AudioLength"], temp["AudioLength-DT"], temp["AudioLength-NC"], temp["AudioLength-HT"] = get_AudioLength(filesinfo, setID, AudioFilename)
        beatmap_info.append(temp)
    beatmap_info = sorted(beatmap_info, key=lambda x: x['BeatmapID'])

    bidsList = [i["BeatmapID"] for i in beatmap_info]
    if int(setID) > 0: first_bid = min([x for x in bidsList if x > 0])
    else: first_bid = min([x for x in bidsList]) #커스텀 비트맵셋일 경우

    try: cheesegull = requests.get(f"https://cheesegull.{osuServerDomain}/api/s/{setID}", headers=requestHeaders).json()
    except: cheesegull = None
    return_result = {"RedstarOSU": [int(setID), first_bid, beatmap_info, file_list], "cheesegull": cheesegull, "Bancho": Bancho}
    threading.Thread(target=saveDB, args=(return_result,)).start()
    if bID is not None:
        redstar = next((b for b in beatmap_info if b["BeatmapID"] == int(bID)), None)
        redstar["files"] = file_list
        gull = next((b for b in cheesegull["ChildrenBeatmaps"] if b["BeatmapID"] == int(bID)), None)
        cho = next((b for b in Bancho if b["beatmap_id"] == bID), None)
        return_result = {"RedstarOSU": redstar, "cheesegull": gull, "Bancho": cho} if redstar and cheesegull else None
    return return_result

def choUnavailable(setID):
    unavailable = False
    audio_unavailable = download_unavailable = storyboard = 0
    Bancho_data = BanchoApiRequest("/api/get_beatmaps", {"s": setID}).json()
    Bancho_data = sorted(Bancho_data, key=lambda x: x['beatmap_id'])
    if not Bancho_data: return {"Bancho_data": None, "unavailable": None, "audio_unavailable": None, "download_unavailable": None, "storyboard": None, "pylist_unavailable": [None, None, None]}
    for i in Bancho_data:
        if int(i["audio_unavailable"]) == 1 and not audio_unavailable:
            unavailable = True
            audio_unavailable = int(i["audio_unavailable"])
            log.error(f"{setID} 셋은 반초에서 음원 없음({audio_unavailable})")
        elif int(i["download_unavailable"]) == 1 and not download_unavailable:
            unavailable = True
            download_unavailable = int(i["download_unavailable"])
            log.error(f"{setID} 셋은 반초에서 다운로드 불가({download_unavailable}) 상태임!!")
        elif int(i["storyboard"]) == 1:
            storyboard = int(i["storyboard"])
        elif audio_unavailable and download_unavailable:
            break
    return {"Bancho_data": Bancho_data, "unavailable": unavailable, "audio_unavailable": audio_unavailable, "download_unavailable": download_unavailable, "storyboard": storyboard, "pylist_unavailable": [audio_unavailable, download_unavailable, storyboard]}
def check(setID, rq_type, checkRenewFile=False, bu = None, bh = None, bvv = None):
    #.osz는 무조건 새로 받되, Bancho, Redstar**전용** 맵에서 ranked, loved 등등 은 새로 안받아도 댐. (Redstar에서의 랭크상태 여부는 고민중)
    #근데 생각해보니 파일 있으면 걍 이걸 안오는데?
    folder_check()
    fullSongName = get_osz_fullName(setID)
    log.debug(fullSongName)
    choData = choUnavailable(setID)

    url = [
        f"https://osu.ppy.sh/d/{setID}?u={Bancho_u}&h={Bancho_p_hashed}",
        f'https://api.nerinyan.moe/d/{setID}',
        #f"https://chimu.moe/d/{setID}",
        f"https://catboy.best/d/{setID}",
        f"https://osu.direct/d/{setID}",
        f"https://beatconnect.io/b/{setID}",
        f"https://txy1.sayobot.cn/beatmaps/download/full/{setID}",
        f"https://storage.ripple.moe/d/{setID}"
    ]
    urlName = ["Bancho", "Nerinyan", "catboy", "osu.direct", "beatconnect", "sayobot", "Ripple"]

    if bu and bh and not choData["unavailable"]:
        url.insert(0, f"https://osu.ppy.sh/d/{setID}?u={bu}&h={bh}&vv={bvv}")
        urlName.insert(0, f"{bu}'s Bancho")

    if choData["unavailable"]:
        log.warning(f"{url[0]} | {urlName[0]} 링크 삭제함!")
        del url[0], urlName[0]

    def dl():
        #우선 setID .osz로 다운받고 나중에 파일 이름 변경
        file_name = f'{setID} .osz' #919187 765 MILLION ALLSTARS - UNION!!.osz, 2052147 (Love Live! series) - Colorful Dreams! Colorful Smiles! _  TV2
        save_path = f'{dataFolder}/dl/'

        for i, (link, mn) in enumerate(zip(url, urlName)):
            # 파일 다운로드 요청
            try:
                res = requests.get(link, headers=requestHeaders, timeout=5, stream=True)
                statusCode = res.status_code
                header_filename = res.headers.get('Content-Disposition')
            except requests.exceptions.ReadTimeout as e:
                log.warning(f"{link} Timeout! | e = {e}")
                statusCode = 504
            except:
                statusCode = res.status_code if res.status_code != 200 else 500
                exceptionE(f"{statusCode} | 파일다운 기본 예외처리 | url = {link}")

            if statusCode == 200 and header_filename:
                file_size = int(res.headers.get('Content-Length', 0)) #파일 크기를 얻습니다.

                # tqdm을 사용하여 진행률 표시
                with open(save_path + file_name, 'wb') as file:
                    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, ncols=120) as pbar:
                        for data in res.iter_content(1024):
                            file.write(data)
                            pbar.update(len(data))

                newFilename = re.findall('filename="([^"]+)"', header_filename)[0]
                if (urlName[i] == "chimu" or urlName[i] == "sayobot") and "%20" in newFilename:
                    newFilename = newFilename.replace("%20", " ")
                newFilename = re.sub(r'[<>:"/\\|?*]', '_', newFilename)

                log.info(f'{file_name} --> {newFilename} 다운로드 완료')

                def play_finished_dl(): #WAV 파일 재생을 별도의 스레드에서 수행
                    os.system(f"ffplay -nodisp -autoexit static/audio/match-confirm.mp3 > {'nul' if OSisWindows else '/dev/null'} 2>&1")
                play_thread = threading.Thread(target=play_finished_dl)
                play_thread.start()

                try:
                    os.rename(f"{dataFolder}/dl/{setID} .osz", f"{dataFolder}/dl/{newFilename}")
                except FileExistsError:
                    ct = int(os.stat(f"{dataFolder}/dl/{newFilename}").st_ctime)
                    shutil.copy2(f"{dataFolder}/dl/{newFilename}", f"{dataFolder}/dl-old/{newFilename[:-4]}-{ct}~{int(time.time())}.osz")
                    os.remove(f"{dataFolder}/dl/{newFilename}")
                    os.replace(f"{dataFolder}/dl/{setID} .osz", f"{dataFolder}/dl/{newFilename}")
                return statusCode
            else:
                if i < len(url) - 1:
                    log.warning(f'{statusCode}. {mn} 에서 파일을 다운로드할 수 없습니다. {urlName[i + 1]} 로 재시도!')
                else:
                    log.warning(f'{statusCode}. {mn} 에서 파일을 다운로드할 수 없습니다!')
                    return statusCode

    if fullSongName == 0:
        log.warning(f"{setID} 맵셋 osz 존재하지 않음. 다운로드중...")
        dlsc = dl()
    elif fullSongName == f'{setID} .osz':
        log.error(f"{fullSongName} | 존재는 하나 꺠지거나 문제가 있음. 재 다운로드중...")
        dlsc = dl()
    else:
        dlsc = 200
        log.info(f"{fullSongName} 존재함")

        with open("exceptOszList.json", "r") as file:
            exceptOszList = json.load(file)
            exceptOszList = exceptOszList["exceptOszList"] + exceptOszList["exceptOszList2"]

        #반초에 먼저 API 요청 때려봄
        try:
            Bancho_LastUpdate = datetime.strptime(choData["Bancho_data"][0]["last_update"], '%Y-%m-%d %H:%M:%S')
            if int(setID) > 0:
                omsDB = dbO.fetch("SELECT last_update, update_lock FROM beatmapsinfo_copy WHERE BeatmapSetID = %s AND BeatmapID > 0 LIMIT 1", [setID])
            else:
                omsDB = dbO.fetch("SELECT last_update, update_lock FROM beatmapsinfo_copy WHERE BeatmapSetID = %s LIMIT 1", [setID])
            if not omsDB: raise
        except: Bancho_LastUpdate,  omsDB = (None, {"last_update": None, "update_lock": 0})
        if omsDB["update_lock"] == 1:
            BanchoTimeCheck = False
        elif not omsDB["last_update"]:
            BanchoTimeCheck = True
        elif Bancho_LastUpdate and omsDB["last_update"] and Bancho_LastUpdate > omsDB["last_update"]:
            BanchoTimeCheck = True
        elif Bancho_LastUpdate is None and omsDB["last_update"] is None:
            BanchoTimeCheck = True #둘다 None 일 경우 그냥 진행함
        else:
            BanchoTimeCheck = False

        #7일 이상 된 비트맵만 파일체크함
        """ fED = os.path.getmtime(f"data/dl/{get_osz_fullName(setID)}")
        t = round(time.time() - fED)
        if t > oszRenewTime:
            fED = True
        else:
            fED = False
        isRenew = checkRenewFile and int(setID) not in exceptOszList and BanchoTimeCheck and fED
        log.info(f"checkRenewFile = {checkRenewFile} | t:{t} > oszRenewTime:{oszRenewTime} = {fED} | exceptOszList = {int(setID) not in exceptOszList} | BanchoTimeCheck = {BanchoTimeCheck} | 최종 조건 = {isRenew}") """

        isRenew = checkRenewFile and int(setID) not in exceptOszList and BanchoTimeCheck
        log.info(f"checkRenewFile = {checkRenewFile} | exceptOszList = {int(setID) not in exceptOszList} | BanchoTimeCheck = {BanchoTimeCheck} | 최종 조건 = {isRenew}")

        #이거 redstar DB에 없는 경우 있으니 cheesegull DB에서도 추가로 참고하기
        if isRenew:
            try:
                rankStatus = dbR.fetch(f"SELECT ranked FROM beatmaps WHERE beatmapset_id = %s", [setID])["ranked"]
                log.info(f"파일 최신화 redstar DB 랭크상태 조회 완료 : {rankStatus}")
                if rankStatus == 4: rankStatus = 0
            except:
                rankStatus = dbC.fetch(f"SELECT ranked_status FROM sets WHERE id = %s", [setID])["ranked_status"]
                log.info(f"파일 최신화 cheesegull DB 랭크상태 조회 완료 : {rankStatus}")
            if rankStatus <= 0:
                oszHash = calculate_md5.file(f"{dataFolder}/dl/{fullSongName}")
                log.debug(f"oszHash = {oszHash}")
                for i, (link, mn) in enumerate(zip(url, urlName)):
                    newOszHash = requests.get(link, headers=requestHeaders, timeout=5, stream=True)
                    header_filename = newOszHash.headers.get('Content-Disposition')
                    if newOszHash.status_code == 200 and header_filename:
                        # tqdm을 사용하여 진행률 표시
                        with open(f"{dataFolder}/dl/t{setID} .osz", 'wb') as file:
                            with tqdm(total=int(newOszHash.headers.get('Content-Length', 0)), unit='B', unit_scale=True, unit_divisor=1024, ncols=60) as pbar:
                                for data in newOszHash.iter_content(1024):
                                    file.write(data)
                                    pbar.update(len(data))
                        newOszHash = calculate_md5.file(f"{dataFolder}/dl/t{setID} .osz")
                        log.debug(f"oszHash = {oszHash} | newOszHash = {newOszHash}")
                        if oszHash != newOszHash:
                            log.warning(f"{setID} 가 최신이 아닙니다!")
                            try:
                                ct = int(os.stat(f"{dataFolder}/dl/{fullSongName}").st_ctime)
                                shutil.copy2(f"{dataFolder}/dl/{fullSongName}", f"{dataFolder}/dl-old/{fullSongName[:-4]}-{ct}~{int(time.time())}.osz")
                            except IOError as e:
                                log.error(f"파일 복사 중 오류 발생: {e}")
                            log.info(f"{removeAllFiles(setID)}\n")
                            os.replace(f"{dataFolder}/dl/t{setID} .osz", f"{dataFolder}/dl/{fullSongName}")
                        else:
                            os.remove(f"{dataFolder}/dl/t{setID} .osz")
                            os.utime(f"{dataFolder}/dl/{fullSongName}", (time.time(), time.time()))
                        break
                    else:
                        if i < len(url) - 1:
                            log.warning(f'{newOszHash.status_code}. {mn} 에서 파일을 다운로드할 수 없습니다. {urlName[i + 1]} 로 재시도!')
                        else:
                            log.warning(f'{newOszHash.status_code}. {mn} 에서 파일을 다운로드할 수 없습니다!')

    if checkRenewFile: #read_osz 전용
        return []
    elif dlsc != 200:
        return dlsc
    else:
        try:
            return osu_file_read(setID, rq_type)["RedstarOSU"]
        except Exception as e:
            return e

#######################################################################################################################################

def read_list(bsid=""):
    result = {}
    if not bsid:
        osz_file_list = [file for file in os.listdir(f"{dataFolder}/dl/") if file.endswith(".osz")]
        files_list = [file for file in os.listdir(f"{dataFolder}/Songs/")]
    else:
        fullSongName = get_osz_fullName(bsid)
        ptct = pathToContentType(fullSongName)
        osz_file_list = [fullSongName]
        files_list = [file for file in os.listdir(f"{dataFolder}/Songs/{ptct['foldername']}")]

    result["osz"] = {"count": len(osz_file_list), "list": osz_file_list}
    result["files"] = {"count": len(files_list), "list": files_list}
    return result

def read_bg(id):
    if "+" in id:
        bsid = int(str(id).replace("+", ""))
        ck = check(bsid, rq_type="bg")
        if type(ck) is int: return ck
        bid = ck[1]
    else:
        bid = int(id)
        try: bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [bid])["parent_set_id"]
        except:
            try:
                bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [bid])["beatmapset_id"]
                log.info("RedstarOSU DB에서 bsid 찾음")
            except: raise KeyError("Not Found bsid!")
        log.info(f"{bid} bid cheesegull db 조회로 {bsid} bsid 얻음")
        ck = check(bsid, rq_type="bg")
        if type(ck) is int: return ck

    fullSongName = get_osz_fullName(bsid)
    ptct = pathToContentType(fullSongName)
    for d in ck[2]:
        if d["BeatmapID"] == bid: return f"{dataFolder}/Songs/{ptct['foldername']}/{d['BeatmapBG']}"

def read_thumb(id):
    if "l.jpg" in id:
        bsid = int(id.replace("l.jpg", ""))
        img_size = (160, 120)
    else:
        bsid = int(id.replace(".jpg", ""))
        img_size = (80, 60)

    ck = check(bsid, rq_type="thumb")
    if type(ck) is int: return ck
    fullSongName = get_osz_fullName(bsid)
    ptct = pathToContentType(fullSongName)
    for d in ck[2]:
        if d["BeatmapID"] == ck[1]: ck = d; break

    if os.path.isfile(f"{dataFolder}/Songs/{ptct['foldername']}/{id}"):
        return f"{dataFolder}/Songs/{ptct['foldername']}/{id}"
    elif os.path.isfile(f"{dataFolder}/Songs/{ptct['foldername']}/noImage_{id}"):
        return f"{dataFolder}/Songs/{ptct['foldername']}/noImage_{id}"
    else:
        with Image.open(f"{dataFolder}/Songs/{ptct['foldername']}/{ck['BeatmapBG']}") as img:
            img = img.convert("RGB")
            width, height = img.size
            if img.size == img_size:
                log.info(f"원본 파일이랑 같은 {img_size} 여서 안짜름")
                shutil.copy2(f"{dataFolder}/Songs/{ptct['foldername']}/{ck['BeatmapBG']}", f"{dataFolder}/Songs/{ptct['foldername']}/{id}")
            elif img.size < img_size:
                log.warning(f"원본 이미지가 더 작음 {img.size}")
                left = round((img_size[0] - width) / 2)
                top = round((img_size[1] - height) / 2)
                right = round(img_size[0] - left)
                bottom = round(img_size[1] - top)

                canvas = Image.new("RGB", img_size, (255, 255, 255))
                canvas.paste(img, (left,top,right,bottom))
                canvas.save(f"{dataFolder}/Songs/{ptct['foldername']}/{id}", quality=100)
            elif width / height == 4 / 3:
                log.info(f"이미 4:3 비율이라서 {img_size} 로만 자름")
                img.resize(img_size, Image.LANCZOS).save(f"{dataFolder}/Songs/{ptct['foldername']}/{id}", quality=100)
            else:
                if width / height > 4 / 3:
                    croped_width = height * (4 / 3) #원본기준 4:3 비율 (width)
                    left = (width - croped_width) / 2
                    top = 0
                    right = width - left
                    bottom = height
                else:
                    croped_height = width / (4 / 3) #원본기준 4:3 비율 (height)
                    left = 0
                    top = (height - croped_height) / 2 # = 160.5
                    right = width
                    bottom = height - top

                img_cropped = img.crop((left,top,right,bottom))
                img_cropped.resize(img_size, Image.LANCZOS).save(f"{dataFolder}/Songs/{ptct['foldername']}/{id}", quality=100)
        return f"{dataFolder}/Songs/{ptct['foldername']}/{id}"

#osu_file_read() 역할 분할하기 (각각 따로 두기)
def read_audio(id, m=None):
    #ffmpeg -i "audio.ogg" -acodec libmp3lame -q:a 0 -y "audio.mp3"
    def audioSpeed(m, setID, ptct, ck):
        #변환 시작 + 에러시 코덱 확인후 재 변환
        file = f"{dataFolder}/Songs/{ptct['foldername']}/{ck['AudioFilename']}"
        Codec = mediainfo(file)["codec_name"]
        if Codec != "mp3": log.error(f"{ck['AudioFilename']} 코텍은 mp3가 아님 | {Codec}")

        try:
            m = int(m)
            if m == mods.DOUBLETIME: m = "DT"
            elif m == mods.NIGHTCORE or m == 576: m = "NC"
            elif m == mods.HALFTIME: m = "HT"
        except: m = m.upper() if m else None

        if m == "DT" and not "noAudio" in ck:
            log.chat("DT 감지")
            DTFilename = f"{file[:-4]}-DT.mp3" if not file.endswith("-DT.mp3") else file
            if os.path.isfile(DTFilename): return DTFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{file}" -af atempo=1.5 -acodec libmp3lame -q:a 0 -y "{DTFilename}"'
                log.chat(f"DT ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return DTFilename
        elif m == "NC" and not "noAudio" in ck:
            log.chat("NC 감지")
            NCFilename = f"{file[:-4]}-NC.mp3" if not file.endswith("-NC.mp3") else file
            if os.path.isfile(NCFilename): return NCFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{file}" -af asetrate={int(mediainfo(file)["sample_rate"])}*1.5 -acodec libmp3lame -q:a 0 -y "{NCFilename}"'
                log.chat(f"NC ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return NCFilename
        elif m == "HT" and not "noAudio" in ck:
            log.chat("HT 감지")
            HTFilename = f"{file[:-4]}-HT.mp3" if not file.endswith("-HT.mp3") else file
            if os.path.isfile(HTFilename): return HTFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{file}" -af atempo=0.75 -acodec libmp3lame -q:a 0 -y "{HTFilename}"'
                log.chat(f"HT ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return HTFilename
        elif m == "PREVIEW" and not "noAudio" in ck:
            log.chat("preview 감지")
            PreviewFilename = f"{file[:-4]}-preview.mp3" if not file.endswith("-preview.mp3") else file
            if os.path.isfile(PreviewFilename): return PreviewFilename
            else:
                if ck["PreviewTime"] == -1:
                    audio = float(mediainfo(file)["duration"])
                    PreviewTime = audio / 2.5
                    log.warning(f"{setID}.mp3 ({ck['AudioFilename']}) 의 PreviewTime 값이 {ck['PreviewTime']} 이므로 TotalLength ({audio}) / 2.5 == {PreviewTime} 로 세팅함")
                else: PreviewTime = ck["PreviewTime"] / 1000

                ffmpeg_msg = f'ffmpeg -i "{file}" -ss {PreviewTime} -acodec libmp3lame -q:a 0 -y "{PreviewFilename}"'
                log.chat(f"preview ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return PreviewFilename
        else: return file

    if "+" in id:
        bsid = int(str(id).replace("+", ""))
        ck = check(bsid, rq_type="audio")
        if type(ck) is int: return ck
        bid = ck[1]
        for d in ck[2]:
            if d["BeatmapID"] == bid: ck = d; break
    else:
        bid = int(id)
        try: bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
        except:
            try:
                bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
                log.info("RedstarOSU DB에서 bsid 찾음")
            except: raise KeyError("Not Found bsid!")
        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
        ck = check(bsid, rq_type="audio")
        if type(ck) is int: return ck
        for d in ck[2]:
            if d["BeatmapID"] == bid: ck = d; break

    fullSongName = get_osz_fullName(bsid)
    ptct = pathToContentType(fullSongName)
    if not os.path.isfile(f"{dataFolder}/Songs/{ptct['foldername']}/{ck['AudioFilename']}") and os.path.isfile(f"{dataFolder}/Songs/{ptct['foldername']}/noAudio.mp3"):
        log.error(f"{bid} bid 실제론 음악파일 없어보이며, noAudio.mp3가 폴더내에 존재함")
        ck = ["noAudio.mp3"]
    return audioSpeed(m, bsid, ptct, ck)

def read_preview(id):
    #source_{bsid}.mp3 먼저 확인시키기 ㄴㄴ audio에서 가져오기
    bsid = int(id.replace(".mp3", ""))
    ck = check(bsid, rq_type="preview")
    if type(ck) is int: return ck
    bid = ck[1]
    for d in ck[2]:
        if d["BeatmapID"] == bid: ck = d; break
    fullSongName = get_osz_fullName(bsid)
    ptct = pathToContentType(fullSongName)

    if os.path.isfile(f"{dataFolder}/Songs/{ptct['foldername']}/{id}"): return f"{dataFolder}/Songs/{ptct['foldername']}/{id}"
    elif os.path.isfile(f"{dataFolder}/Songs/{ptct['foldername']}/noAudio_{id}"):
        #위에서 오디오 없어서 이미 처리댐 (noAudio_{setID}.mp3)
        log.warning(f"noAudio_{id}")
        return f"{dataFolder}/Songs/{ptct['foldername']}/noAudio_{id}"
    else:
        #음원 하이라이트 가져오기, 밀리초라서 / 1000 함
        file = f"{dataFolder}/Songs/{ptct['foldername']}/{ck['AudioFilename']}"
        Codec = mediainfo(f"{file}")["codec_name"]
        if Codec != "mp3": log.error(f"{ck['AudioFilename']} 코텍은 mp3가 아님 | {Codec}")

        audio = float(mediainfo(file)["duration"])
        if ck["PreviewTime"] == -1:
            PreviewTime = audio / 2.5
            log.warning(f"{bsid}.mp3 ({ck['AudioFilename']}) 의 PreviewTime 값이 {ck['PreviewTime']} 이므로 TotalLength ({audio}) / 2.5 == {PreviewTime} 로 세팅함")
        elif ck["PreviewTime"] / 1000 > audio:
            PreviewTime = 0
            log.warning(f'PreviewTime({ck["PreviewTime"] / 1000}) 이 > audio({float(mediainfo(file)["duration"])}) 보다 길어서 0으로 세팅함') #666438.mp3
        else:  PreviewTime = ck["PreviewTime"] / 1000

        if Codec == "mp3": ffmpeg_msg = f'ffmpeg -i "{file}" -ss {PreviewTime} -t 30.821 -acodec copy -y "{dataFolder}/Songs/{ptct["foldername"]}/{id}"'
        else:
            ffmpeg_msg = f'ffmpeg -i "{file}" -ss {PreviewTime} -t 30.821 -acodec libmp3lame -q:a 0 -y "{dataFolder}/Songs/{ptct["foldername"]}/{id}"'
            log.warning(f"ffmpeg_msg = {ffmpeg_msg}")

        log.chat(f"ffmpeg_msg = {ffmpeg_msg}")
        os.system(ffmpeg_msg)
        return f"{dataFolder}/Songs/{ptct['foldername']}/{id}"

def read_video(id):
    bid = int(id)
    try:
        bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [bid])["parent_set_id"]
        log.info(f"{bid} bid cheesegull db 조회로 {bsid} bsid 얻음")
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [bid])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except:  raise KeyError("Not Found bsid!")
    ck = check(bsid, rq_type="video")
    if type(ck) is int: return ck
    for d in ck[2]:
        if d["BeatmapID"] == bid: ck = d; break
    fullSongName = get_osz_fullName(bsid)
    ptct = pathToContentType(fullSongName)

    hasVideo = ck["BeatmapVideo"]
    if hasVideo is None:
        log.warning(f"{id} 해당 비트맵은 .osu 파일에 비디오 정보가 없습니다!")
        try:
            #hasVideo = dbC.fetch("SELECT has_video FROM sets WHERE id = %s", [bsid])["has_video"]
            #반초로 조회함
            hasVideo = int(BanchoApiRequest("/api/get_beatmaps", {"b": id}).json()[0]["video"])
            if hasVideo != 0: return f"{dataFolder}/Songs/{ptct['foldername']}/{ck['BeatmapVideo']}"
            else: raise
        except: return f"{id} Beatmap has no video!"
    else:
        #임시로 try 박아둠, 나중에 반초라던지 비디오 있나 요청하는거로 바꾸기
        if os.path.isfile(f"{dataFolder}/Songs/{ptct['foldername']}/{hasVideo}"): return f"{dataFolder}/Songs/{ptct['foldername']}/{hasVideo}"

def read_osz(id, u = None, h = None, vv = None):
    check(id, rq_type="osz", checkRenewFile=True, bu=u, bh=h, bvv=vv)
    filename = get_osz_fullName(id)
    if filename != f"{id} .osz" and os.path.isfile(f"{dataFolder}/dl/{filename}"): return f"{dataFolder}/dl/{filename}"
    else: return 0

def read_osz_b(id):
    try: bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except: raise KeyError("Not Found bsid!")
    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
    return read_osz(bsid)

def read_osu(id):
    bid = int(id)
    try: bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [bid])["parent_set_id"]
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [bid])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except: raise KeyError("Not Found bsid!")
    log.info(f"{bid} bid cheesegull db 조회로 {bsid} bsid 얻음")

    ck = check(bsid, rq_type=f"read_osu_{bid}")
    if type(ck) is int: return ck
    for d in ck[2]:
        if d["BeatmapID"] == bid: ck = d; break
    fullSongName = get_osz_fullName(bsid)
    ptct = pathToContentType(fullSongName)
    return f"{dataFolder}/Songs/{ptct['foldername']}/{ck['beatmapName']}"

def filename_to_GetCheesegullDB(filename):
    try:
        pattern = r'^(?P<artist>.+) - (?P<title>.+) \((?P<creator>.+)\) \[(?P<version>.+)\]\.osu$'
        match = re.match(pattern, filename)
        artist = match.group('artist')
        title = match.group('title')
        creator = match.group('creator')
        version = match.group('version')
    except:
        artist, title, creator, version = None
        log.error("osu filename에서 artist, title, creator, version 추출중 에러")

    #osu_media_server DB 로 먼저 뽑아봄
    log.debug(f"filename = {filename} | {artist}, {title}, {creator}, {version}")
    resu = dbO.fetch("SELECT BeatmapID as id, BeatmapSetID as parent_set_id FROM beatmapsinfo_copy WHERE file_name = %s", [filename])
    if resu: return resu

    #위에 코드로 대채 테스트
    """ try:
        parentheses = filename.count(" (")
        if parentheses == 1:
            # 정규식 패턴, 일반적인 경우
            pattern = r"^(.+) - (.+) \(([^)]+)\) \[([^]]+)\]\.osu$"
            match = re.match(pattern, filename)

            artist = match.group(1)
            title = match.group(2)
            creator = match.group(3)
            version = match.group(4)
        elif parentheses == 0:
            # 정규식 패턴, 제작자 누락된 경우
            pattern = r"^(.+) - (.+) \[([^]]+)\]\.osu$"
            match = re.match(pattern, filename)

            artist = match.group(1)
            title = match.group(2)
            creator = match.group(3)
            version = match.group(4)
        else:
            # 정규식 패턴, 괄호가 하나 더 있어서 에러방지
            pattern = r"^(.+) - (.+) (\([^()]+\)) \(([^()]+)\) \[([^]]+)\]\.osu$"
            match = re.match(pattern, filename)

            artist = match.group(1)
            title = f"{match.group(2)} {match.group(3)}"
            creator = match.group(4)
            version = match.group(5)
    except:
        artist = None
        title = None
        creator = None
        version = None
        log.error("osu filename에서 artist, title, creator, version 추출중 에러") """

    """ try:
        artist = filename[:filename.find(" - ")]
        title = filename[(filename.find(" - ") + 3):filename.find(" (")]
        creator = filename[(filename.find(" (") + 1 + 1):(filename.find(") ["))]
        version = filename[(filename.find(") [") + 1 + 2):filename.find("].osu")]
    except:
        log.error("osu filename에서 artist, title, creator, version 추출중 에러") """

    # filename에 / 가 들어가면 에러남 (http 요청시 / 가 사라짐)
    sql = '''
        SELECT b.id, b.parent_set_id, b.file_md5, b.diff_name, s.ranked_status
        FROM beatmaps AS b
        JOIN sets AS s ON b.parent_set_id = s.id
        WHERE s.artist = %s AND s.title = %s AND s.creator = %s AND b.diff_name = %s
    '''
    result = dbC.fetch(sql, [artist, title, creator, version])
    if result is None:
        #특수문자 등등 조회 안되는거 짤라서 조회
        log.warning(f"filename 조회 실패! | 단어별로 짤라서 찾아봄 | {filename}")

        artist_sp = artist.split()
        title_sp = title.split()
        creator_sp = creator.split()
        version_sp = version.split()

        sql_part = '''
            SELECT b.id, b.parent_set_id, b.file_md5, b.diff_name, s.ranked_status
            FROM cheesegull.beatmaps AS b
            JOIN cheesegull.sets AS s ON b.parent_set_id = s.id
            WHERE TRUE
        '''
        param_part = []
        for i, v in enumerate(artist_sp):
            sql_part += " AND s.artist LIKE %s"
            if len(artist_sp) == 1: param_part.append(v)
            elif i == 0 and i != len(artist_sp) - 1: param_part.append(f"{v}%")
            elif i == len(artist_sp) - 1: param_part.append(f"%{v}")
            else: param_part.append(f"%{v}%")
        for i, v in enumerate(title_sp):
            sql_part += " AND s.title LIKE %s"
            if len(title_sp) == 1: param_part.append(v)
            elif i == 0 and i != len(title_sp) - 1: param_part.append(f"{v}%")
            elif i == len(title_sp) - 1: param_part.append(f"%{v}")
            else: param_part.append(f"%{v}%")
        for i, v in enumerate(creator_sp):
            sql_part += " AND s.creator LIKE %s"
            if len(creator_sp) == 1: param_part.append(v)
            elif i == 0 and i != len(creator_sp) - 1: param_part.append(f"{v}%")
            elif i == len(creator_sp) - 1: param_part.append(f"%{v}")
            else: param_part.append(f"%{v}%")
        for i, v in enumerate(version_sp):
            sql_part += " AND b.diff_name LIKE %s"
            if len(version_sp) == 1: param_part.append(v)
            elif i == 0: param_part.append(f"{v}%")
            elif i == len(version_sp) - 1: param_part.append(f"%{v}")
            else: param_part.append(f"%{v}%")

        result_part = dbC.fetch(sql_part, param_part)
        if result_part is None:
            return None
        elif type(result_part) == list and len(result_part) > 1:
            log.warning(f"값이 2개 이상임 ({len(result_part)}) | result_part = {result_part}")
            return None
        else:
            return result_part
    else:
        return result

def read_osu_filename(filename):
    for root, dirs, files in os.walk(f"{dataFolder}/Songs"): #파일 찾기 실행
        if filename in files:
            try:
                bsid = int(pathToContentType(root)["filename"].split(" ")[0])
                #ck = check(bsid, rq_type="all") #업데이트 확인용
                #if type(ck) is int: return ck
            except: bsid = None
            return os.path.join(root, filename)

    result = filename_to_GetCheesegullDB(filename)
    log.debug(f"result = {result}")
    if result is None:
        #Bancho에 이름으로 bid 찾는 방법 찾아내기
        return None
    bid = result["id"]
    return read_osu(bid)

def read_raw(folder, file):
    if os.path.isfile(f"{dataFolder}/Songs/{folder}/{file}"): return f"{dataFolder}/Songs/{folder}/{file}"
    else:
        bsid = int(folder.split(" ")[0])
        ck = check(bsid, rq_type="all")
        if os.path.isfile(f"{dataFolder}/Songs/{folder}/{file}"): return f"{dataFolder}/Songs/{folder}/{file}"

def read_covers(id, cover_type):
    if not os.path.isfile(f"{dataFolder}/covers/{id}/{cover_type}"):
        try:
            result = requests.get(f"https://assets.ppy.sh/beatmaps/{id}/covers/{cover_type}", headers=requestHeaders)
            if result.status_code == 200:
                os.makedirs(f"{dataFolder}/covers/{id}", exist_ok=True) #디렉토리가 존재하지 않으면 생성
                with open(f"{dataFolder}/covers/{id}/{cover_type}", "wb") as file:
                    file.write(result.content)
                return f"{dataFolder}/covers/{id}/{cover_type}"
            else:
                return result.status_code
        except:
            log.error(f"{id}, {cover_type} | covers 처리중 에러발생!")
            exceptionE("")
            return 503
    else:
        return f"{dataFolder}/covers/{id}/{cover_type}"

def removeAllFiles(bsid):
    #osu-media-server DB 테이블에서 확인후 존재하면 삭제하기

    osz = get_osz_fullName(bsid)
    ptct = pathToContentType(osz)

    isdelosz = isdelfiles = 0
    print("")

    #osz
    if osz == 0: log.error(f"{bsid} osz는 존재하지 않음")
    else:
        try:
            os.remove(f"{dataFolder}/dl/{osz}")
            log.info(f'파일 {osz} 가 삭제되었습니다.')
            isdelosz = 1
        except OSError as e: log.error(f'파일 삭제 실패: {e}')

    #files
    try:
        shutil.rmtree(f"{dataFolder}/Songs/{ptct['foldername']}")
        log.info(f"폴더 {dataFolder}/Songs/{ptct['foldername']} 가 삭제되었습니다.")
        isdelfiles = 1
    except: pass

    return {"message": {0: "Doesn't exist", 1: "Delete success"} , "name": osz, "osz": isdelosz, "files": isdelfiles}