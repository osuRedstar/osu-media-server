from lets_common_log import logUtils as log
from dbConnent import db
import zipfile
import os
import shutil
import requests
from tqdm import tqdm
import config
from PIL import Image
import hashlib
import re
from pydub.utils import mediainfo
import threading
import time
from datetime import datetime
import json
from collections import Counter
import subprocess
import geoip2.database
import mods

class calculate_md5:
    @classmethod
    def file(cls, fn) -> str:
        md5 = hashlib.md5()
        with open(fn, "rb") as f:
            md5.update(f.read())
        return md5.hexdigest()

    @classmethod
    def text(cls, t) -> str:
        md5 = hashlib.md5()
        md5.update(t.encode("utf-8"))
        return md5.hexdigest()

conf = config.config("config.ini")
OSU_APIKEY = conf.config["osu"]["Bancho_Apikey"]
Bancho_u = conf.config["osu"]["Bancho_username"]
Bancho_p = conf.config["osu"]["Bancho_password"]
Bancho_p_hashed = calculate_md5.text(Bancho_p)
#lets.py 형태의 사설서버를 소유중이면 lets\.data\beatmaps 에서만 .osu 파일을 가져옴
IS_YOU_HAVE_OSU_PRIVATE_SERVER = conf.config["osu"]["IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py"]
IS_YOU_HAVE_OSU_PRIVATE_SERVER = False if IS_YOU_HAVE_OSU_PRIVATE_SERVER.lower() == "false" or IS_YOU_HAVE_OSU_PRIVATE_SERVER == "0" else True
lets_beatmaps_Folder = conf.config["osu"]["lets.py_beatmaps_Folder_Path"]
dataFolder = conf.config["server"]["dataFolder"]
oszRenewTime = int(conf.config["server"]["oszRenewTime"])
osuServerDomain = conf.config["server"]["osuServerDomain"]

dbR = db(conf.config["db"]["database"])
dbC = db("cheesegull")
dbO = db("osu_media_server")

requestHeaders = {"User-Agent": f"RedstarOSU's MediaServer (python requests) | https://b.{osuServerDomain}"}

#API 키 테스트
log.info("Bancho apikeyStatus check...")
apikeyStatus = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_APIKEY}&b=-1", headers=requestHeaders)
if apikeyStatus.status_code != 200:
    log.warning("[!] Bancho apikey does not work.")
    log.warning("[!] Please edit your config.ini and run the server again.")
    exit()
log.info("Done!")

#ffmpeg 설치확인
if os.system(f"ffmpeg -version > {'nul' if os.name == 'nt' else '/dev/null'} 2>&1") != 0:
    log.warning(f"ffmpeg Does Not Found!! | ignore? (y/n) ")
    if input("").lower() != "y":
        print("exit")
        if os.name != "nt":
            print("sudo apt install ffmpeg")
        else:
            print("https://github.com/BtbN/FFmpeg-Builds/releases")
        exit()
    else:
        print("ignored")
        log.warning("Maybe Not work preview & audio (DT, NC, HT)")

####################################################################################################

# main.py
ContectEmail = conf.config["server"]["ContectEmail"]
allowedconnentedbot = conf.config["server"]["allowedconnentedbot"]
if allowedconnentedbot == "True" or allowedconnentedbot == "1":
    allowedconnentedbot = True
    log.chat("봇 접근 허용")
else:
    allowedconnentedbot = False
    log.warning("봇 접근 거부")

def getRequestInfo(self):
    IsCloudflare = False
    IsNginx = False
    IsHttp = False
    try:
        real_ip = self.request.headers["Cf-Connecting-Ip"]
        request_url = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
        country_code = self.request.headers["Cf-Ipcountry"]
        IsCloudflare = True
        IsNginx = True
        Server = "Cloudflare"
    except Exception as e:
        log.warning(f"cloudflare를 거치지 않음, real_ip는 nginx header에서 가져옴 | e = {e}")
        try:
            real_ip = self.request.headers["X-Real-Ip"]
            request_url = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
            IsNginx = True
            Server = subprocess.check_output(["nginx.exe", "-v"], stderr=subprocess.STDOUT).decode().strip().split(":")[1].strip()
        except Exception as e:
            log.warning(f"http로 접속시도함 | cloudflare를 거치지 않음, real_ip는 http요청이라서 바로 뜸 | e = {e}")
            real_ip = self.request.remote_ip
            request_url = self.request.protocol + "://" + self.request.host + self.request.uri
            IsHttp = True
            Server = self._headers.get("Server")

        #2자리 국가코드
        reader = geoip2.database.Reader("GeoLite2-Country.mmdb")
        try:
            country_code = reader.country(real_ip).country.iso_code
        except geoip2.errors.AddressNotFoundError:
            country_code = "XX"
            log.error(f"주어진 IP 주소 : {real_ip} 를 찾을 수 없습니다.")
        except Exception as e:
            country_code = "XX"
            log.error("국가코드 오류 발생:", e)

    client_ip = self.request.remote_ip

    try:
        User_Agent = self.request.headers["User-Agent"]
    except:
        User_Agent = ""
        log.error("User-Agent 값이 존재하지 않음!")

    try:
        Referer = self.request.headers["Referer"]
        log.info("Referer 값이 존재함!")
    except:
        Referer = ""

    return real_ip, request_url, country_code, client_ip, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server

def request_msg(self, botpass=False):
    # Logging the request IP address
    print("")
    
    real_ip, request_url, country_code, client_ip, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server = getRequestInfo(self)

    def logmsg(msg):
        if botpass:
            log.warning(msg)
        else:
            log.error(msg)

    #필?터?링
    if allowedconnentedbot:
        log.info(f"Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
        return 200
    else:
        with open("botList.json", "r") as f:
            botList = json.load(f)
            if any(i in User_Agent.lower() for i in botList["no"]) and not any(i in User_Agent.lower() for i in botList["ok"]):
                logmsg(f"bot 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
                return "bot"
            elif "python-requests" in User_Agent.lower():
                logmsg(f"python-requests 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
                return "python-requests"
            elif "python-urllib" in User_Agent.lower():
                logmsg(f"Python-urllib 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
                return "Python-urllib"

            elif any(i in User_Agent.lower() for i in botList["ok"]):
                log.info(f"bot 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
                return 200
            elif "postmanruntime" in User_Agent.lower():
                log.debug(f"PostmanRuntime 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
                return 200
            elif User_Agent == "osu!":
                log.info(f"osu! 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
                return 200
            else:
                log.info(f"Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_url} | From: {User_Agent} | Referer: {Referer}")
                return 200

def resPingMs(self):
    pingMs = (time.time() - self.request._start_time) * 1000
    log.chat(f"{pingMs} ms")
    return pingMs

def send401(self, errMsg):
    self.set_status(401)
    self.set_header("Content-Type", "application/json")
    self.write(json.dumps({"code": 401, "error": errMsg}, indent=2, ensure_ascii=False))
    self.set_header("Ping", str(resPingMs(self)))

def send403(self, rm):
    self.set_status(403)
    self.set_header("Content-Type", "application/json")
    self.write(json.dumps({"code": 403, "error": f"{rm} is Not allowed!!", "message": f"contect --> {ContectEmail}"}, indent=2, ensure_ascii=False))
    self.set_header("Ping", str(resPingMs(self)))

def send404(self, inputType, input):
    self.set_status(404)
    self.set_header("return-fileinfo", json.dumps({"filename": "404.html", "path": "templates/404.html", "fileMd5": calculate_md5.file("templates/404.html")}))
    self.render("templates/404.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

def send500(self, inputType, input):
    self.set_status(500)
    self.set_header("return-fileinfo", json.dumps({"filename": "500.html", "path": "templates/500.html", "fileMd5": calculate_md5.file("templates/500.html")}))
    self.render("templates/500.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

def send503(self, e, inputType, input):
    self.set_status(503)
    #Exception = json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False)
    self.set_header("Exception", json.dumps({"type": str(type(e)), "error": str(e)}))
    self.set_header("return-fileinfo", json.dumps({"filename": "503.html", "path": "templates/503.html", "fileMd5": calculate_md5.file("templates/503.html")}))
    self.render("templates/503.html", inputType=inputType, input=input, Exception=json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False))
    self.set_header("Ping", str(resPingMs(self)))

def send504(self, inputType, input):
    #cloudflare 504 페이지로 연결됨
    self.set_status(504)
    self.set_header("return-fileinfo", json.dumps({"filename": "504.html", "path": "templates/504.html", "fileMd5": calculate_md5.file("templates/504.html")}))
    self.render("templates/504.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

def IDM(self, path):
    if "Range" in self.request.headers and path.endswith(".osz"): #audio html 음악 안나옴 이슈 있음
        idm = True
        log.info("분할 다운로드 활성화!")
        Range = self.request.headers["Range"].replace("bytes=", "").split("-")
        fileSize = os.path.getsize(path)
        start = int(Range[0])
        end = os.path.getsize(path) - 1 if not Range[1] else int(Range[1])
        contentLength = end - start + 1

        self.set_status(206) if start != 0 or (start == 0 and Range[1]) else self.set_status(200)
        self.set_header("Content-Length", contentLength)
        self.set_header("Content-Range", f"bytes={start}-{end}/{fileSize}")
        log.info({"Content-Range": f"bytes={start}-{end}/{fileSize}", "Content-Length": contentLength})

        with open(path, "rb") as f:
            f.seek(start) if start != 0 or (start == 0 and Range[1]) else ""
            file = f.read(contentLength) if start != 0 or (start == 0 and Range[1]) else f.read()
            self.write(file)
    else:
        idm = False
        with open(path, 'rb') as f:
            self.write(f.read())

    filename = path.split("/")[len(path.split("/")) - 1]
    self.set_header('Content-Disposition', f'inline; filename="{filename}"')
    self.set_header("Accept-Ranges", "bytes")
    return idm

def pathToContentType(path, isInclude=False):
    fn, fe = os.path.splitext(os.path.basename(path))
    if isInclude and ".aac" in path or not isInclude and path.endswith(".aac"): return {"Content-Type": "audio/aac", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".apng" in path or not isInclude and path.endswith(".apng"): return {"Content-Type": "image/apng", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".avif" in path or not isInclude and path.endswith(".avif"): return {"Content-Type": "image/avif", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".avi" in path or not isInclude and path.endswith(".avi"): return {"Content-Type": "video/x-msvideo", "filename": fn, "extension": fe, "type": "video", "path": path}
    if isInclude and ".bin" in path or not isInclude and path.endswith(".bin"): return {"Content-Type": "application/octet-stream", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".css" in path or not isInclude and path.endswith(".css"): return {"Content-Type": "text/css", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".gif" in path or not isInclude and path.endswith(".gif"): return {"Content-Type": "image/gif", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".html" in path or not isInclude and path.endswith(".html"): return {"Content-Type": "text/html", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".ico" in path or not isInclude and path.endswith(".ico"): return {"Content-Type": "image/x-icon", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".jfif" in path or not isInclude and path.endswith(".jfif"): return {"Content-Type": "image/jpeg", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".jpeg" in path or not isInclude and path.endswith(".jpeg"): return {"Content-Type": "image/jpeg", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".jpg" in path or not isInclude and path.endswith(".jpg"): return {"Content-Type": "image/jpeg", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".js" in path or not isInclude and path.endswith(".js"): return {"Content-Type": "text/javascript", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".json" in path or not isInclude and path.endswith(".json"): return {"Content-Type": "application/json", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".mp3" in path or not isInclude and path.endswith(".mp3"): return {"Content-Type": "audio/mpeg", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".mp4" in path or not isInclude and path.endswith(".mp4"): return {"Content-Type": "video/mp4", "filename": fn, "extension": fe, "type": "video", "path": path}
    if isInclude and ".mpeg" in path or not isInclude and path.endswith(".mpeg"): return {"Content-Type": "audio/mpeg", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".oga" in path or not isInclude and path.endswith(".oga"): return {"Content-Type": "audio/ogg", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".ogg" in path or not isInclude and path.endswith(".ogg"): return {"Content-Type": "application/ogg", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".ogv" in path or not isInclude and path.endswith(".ogv"): return {"Content-Type": "video/ogg", "filename": fn, "extension": fe, "type": "video", "path": path}
    if isInclude and ".ogx" in path or not isInclude and path.endswith(".ogx"): return {"Content-Type": "application/ogg", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".opus" in path or not isInclude and path.endswith(".opus"): return {"Content-Type": "audio/opus", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".png" in path or not isInclude and path.endswith(".png"): return {"Content-Type": "image/png", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".svg" in path or not isInclude and path.endswith(".svg"): return {"Content-Type": "image/svg+xml", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".tif" in path or not isInclude and path.endswith(".tif"): return {"Content-Type": "image/tiff", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".tiff" in path or not isInclude and path.endswith(".tiff"): return {"Content-Type": "image/tiff", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".ts" in path or not isInclude and path.endswith(".ts"): return {"Content-Type": "video/mp2t", "filename": fn, "extension": fe, "type": "video", "path": path}
    if isInclude and ".txt" in path or not isInclude and path.endswith(".txt"): return {"Content-Type": "text/plain", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".wav" in path or not isInclude and path.endswith(".wav"): return {"Content-Type": "audio/wav", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".weba" in path or not isInclude and path.endswith(".weba"): return {"Content-Type": "audio/webm", "filename": fn, "extension": fe, "type": "audio", "path": path}
    if isInclude and ".webm" in path or not isInclude and path.endswith(".webm"): return {"Content-Type": "video/webm", "filename": fn, "extension": fe, "type": "video", "path": path}
    if isInclude and ".webp" in path or not isInclude and path.endswith(".webp"): return {"Content-Type": "image/webp", "filename": fn, "extension": fe, "type": "image", "path": path}
    if isInclude and ".zip" in path or not isInclude and path.endswith(".zip"): return {"Content-Type": "application/zip", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".flv" in path or not isInclude and path.endswith(".flv"): return {"Content-Type": "video/x-flv", "filename": fn, "extension": fe, "type": "video", "path": path}
    if isInclude and ".wmv" in path or not isInclude and path.endswith(".wmv"): return {"Content-Type": "video/x-ms-wmv", "filename": fn, "extension": fe, "type": "video", "path": path}
    if isInclude and ".mkv" in path or not isInclude and path.endswith(".mkv"): return {"Content-Type": "video/x-matroska", "filename": fn, "extension": fe, "type": "video", "path": path}

    if isInclude and ".osz" in path or not isInclude and path.endswith(".osz"): return {"Content-Type": "application/x-osu-beatmap-archive", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".osr" in path or not isInclude and path.endswith(".osr"): return {"Content-Type": "application/x-osu-replay", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".osu" in path or not isInclude and path.endswith(".osu"): return {"Content-Type": "application/x-osu-beatmap", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".osb" in path or not isInclude and path.endswith(".osb"): return {"Content-Type": "application/x-osu-storyboard", "filename": fn, "extension": fe, "type": "file", "path": path}
    if isInclude and ".osk" in path or not isInclude and path.endswith(".osk"): return {"Content-Type": "application/x-osu-skin", "filename": fn, "extension": fe, "type": "file", "path": path}

    else: return {"Content-Type": "application/octet-stream", "filename": fn, "extension": fe, "type": "?", "path": path}
    
    

####################################################################################################
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
            AudioLength = round(float(mediainfo(f"{dataFolder}/dl/{setID}/{AudioFilename}")["duration"]), 2)
            AudioLength = [AudioLength, culc_length(round(AudioLength))]
            AudioLength_DT = AudioLength_NC = [round(AudioLength[0] / 1.5, 2), culc_length(round(AudioLength[0] / 1.5))]
            #HT = 1. (AudioLength / 0.75), 2. (AudioLength * 1.5)
            AudioLength_HT = [round(AudioLength[0] / 0.75, 2), culc_length(round(AudioLength[0] / 0.75))]
        else:
            AudioLength = AudioLength_DT = AudioLength_NC = AudioLength_HT = None
    except:
        AudioLength = AudioLength_DT = AudioLength_NC = AudioLength_HT = None
    return (AudioLength, AudioLength_DT, AudioLength_NC, AudioLength_HT)

def get_dir_size(path='.'):
    total = 0
    stack = [path]
    while stack:
        current_path = stack.pop()
        for entry in os.scandir(current_path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                stack.append(entry.path)
    if total < 1024:
        return f"{total} Byte"
    if total / (1024 ** 1) < 1024:
        return f"{round(total / (1024 ** 1), 2)} KB"
    if total / (1024 ** 2) < 1024:
        return f"{round(total / (1024 ** 2), 2)} MB"
    if total / (1024 ** 3) < 1024:
        return f"{round(total / (1024 ** 3), 2)} GB"
    if total / (1024 ** 4) < 1024:
        return f"{round(total / (1024 ** 4), 2)} TB"

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
    if not os.path.isdir(f"{dataFolder}/audio"):
        os.mkdir(f"{dataFolder}/audio")
        log.info(f"{dataFolder}/audio 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/preview"):
        os.mkdir(f"{dataFolder}/preview")
        log.info(f"{dataFolder}/preview 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/video"):
        os.mkdir(f"{dataFolder}/video")
        log.info(f"{dataFolder}/video 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/thumb"):
        os.mkdir(f"{dataFolder}/thumb")
        log.info(f"{dataFolder}/thumb 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/bg"):
        os.mkdir(f"{dataFolder}/bg")
        log.info(f"{dataFolder}/bg 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/osu") and not IS_YOU_HAVE_OSU_PRIVATE_SERVER:
        os.mkdir(f"{dataFolder}/osu")
        log.info(f"{dataFolder}/osu 폴더 생성")

def get_osz_fullName(setID):
    try:
        fullName = [file for file in os.listdir(f"{dataFolder}/dl/") if file.startswith(f"{setID} ")][0]
        return fullName
    except:
        return 0

def osu_file_read(setID, rq_type, moving=False, bID=None, cheesegull=False, filesinfo=False):
    #/filesinfo 조회시 osz 없을때 오류 방지
    if get_osz_fullName(setID) == 0 and rq_type == "all":
        ck = check(setID, rq_type)
        if type(ck) is not list:
            return ck

    #압축파일에 문제생겼을때 재 다운로드
    try:
        zipfile.ZipFile(f'{dataFolder}/dl/{get_osz_fullName(setID)}').extractall(f'{dataFolder}/dl/{setID}')
    except zipfile.BadZipFile as e:
        ck = check(setID, rq_type)
        if type(ck) is not list:
            return ck
        try:
            zipfile.ZipFile(f'{dataFolder}/dl/{get_osz_fullName(setID)}').extractall(f'{dataFolder}/dl/{setID}')
        except zipfile.BadZipFile as e:
            log.error(f"압축파일 오류: {e}")

    oszHash = calculate_md5.file(f"{dataFolder}/dl/{get_osz_fullName(setID)}")
    file_list = os.listdir(f"{dataFolder}/dl/{setID}")
    file_list_osu = [file for file in file_list if file.endswith(".osu")]

    beatmap_info = []
    underV10 = False

    #.osu 파일명 기준으로 이름순으로 정렬함
    gullDB = dbC.fetch("""
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
        beatmap_md5 = calculate_md5.file(f"{dataFolder}/dl/{setID}/{beatmapName}")

        sql = """
            SELECT file_name as beatmapName, BeatmapMD5, osu_file_format_v, AudioFilename,
                PreviewTime, Version, BeatmapID, BeatmapBG,
                BeatmapVideo, audio_unavailable, download_unavailable, storyboard
            FROM beatmapsinfo_copy WHERE BeatmapMD5 = %s
        """
        temp = omsDB = dbO.fetch(sql, [beatmap_md5], NoneMsg=False)
        if not temp: temp = {}

        if temp:
            temp["AudioLength"], temp["AudioLength-DT"], temp["AudioLength-NC"], temp["AudioLength-HT"] = get_AudioLength(filesinfo, setID, temp["AudioFilename"])
            log.debug((temp, omsDB, oszUpdateCheck))
        else:
            with open(f"{dataFolder}/dl/{setID}/{beatmapName}", 'r', encoding="utf-8") as f:
                line = f.read()

                line = line[line.find("osu file format v"):]
                try:
                    osu_file_format_version = int(line.split("\n")[:4][0].replace("osu file format v", "").replace(" ", ""))
                except:
                    osu_file_format_version = 0
                if osu_file_format_version == 0:
                    log.error("osu file format v0")
                elif osu_file_format_version < 10:
                    underV10 = True
                    log.error(f"{setID} 비트맵셋의 어떤 비트맵은 시이이이이발 osu file format 이 10이하 ({osu_file_format_version}) 이네요? 시발련들아?")
                    #틀딱곡 BeatmapID 를 Version 쪽에 넘김

                line = line[line.find("AudioFilename:"):]
                try:
                    AudioFilename = line.split("\n")[:4][0].replace("AudioFilename:", "")
                    AudioFilename = AudioFilename.replace(" ", "", 1) if AudioFilename.startswith(" ") else AudioFilename
                except:
                    AudioFilename = None

                line = line[line.find("PreviewTime:"):]
                try:
                    PreviewTime = line.split("\n")[:4][0].replace("PreviewTime:", "")
                    PreviewTime = int(PreviewTime.replace(" ", "", 1) if PreviewTime.startswith(" ") else PreviewTime)
                except:
                    PreviewTime = None
                
                line = line[line.find("Version:"):]
                try:
                    Version = line.split("\n")[:4][0].replace("Version:", "")
                    Version = Version.replace(" ", "", 1) if Version.startswith(" ") else Version
                except:
                    Version = None

                if osu_file_format_version >= 10:
                    line = line[line.find("BeatmapID:"):]
                    try:
                        BeatmapID = line.split("\n")[:4][0].replace("BeatmapID:", "")
                        BeatmapID = int(BeatmapID.replace(" ", "", 1) if BeatmapID.startswith(" ") else BeatmapID)

                        #.osu 파일에서 실제로 존재하지 않거나, 맞지않는 bid 가 있어서 점검함
                        for i in gullDB if type(gullDB) == list else [gullDB]:
                            if i["file_md5"] == beatmap_md5 and BeatmapID != i["id"]:
                                log.error(f"비트맵ID 정보 서로 일치하지 않음 | [{i['diff_name']}] | BeatmapID = {BeatmapID} <-- i['id'] = {i['id']}")
                                BeatmapID = i["id"]
                    except:
                        BeatmapID = 0
                else:
                    log.warning(f"osu file format v{osu_file_format_version} | files bid = 0")
                    BeatmapID = 0

                line = line[line.find("//Background and Video events"):]
                try:
                    BeatmapVideo = BeatmapBG = None
                    lineSpilted = line.split("\n")[:4]
                    for p in lineSpilted:
                        t = pathToContentType(p, isInclude=True)
                        if t["type"] == "video": BeatmapVideo = p[p.find('"') + 1 : p.find('"', p.find('"') + 1)]
                        elif t["type"] == "image": BeatmapBG = p[p.find('"') + 1 : p.find('"', p.find('"') + 1)]
                except:
                    BeatmapBG = BeatmapVideo = None

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
                temp["storyboard"] = storyboard
                temp["AudioLength"], temp["AudioLength-DT"], temp["AudioLength-NC"], temp["AudioLength-HT"] = get_AudioLength(filesinfo, setID, AudioFilename)
        beatmap_info.append(temp)

    bidsList = [i["BeatmapID"] for i in beatmap_info]
    md5sList = [i["BeatmapMD5"] for i in beatmap_info]
    verList = [i["Version"] for i in beatmap_info]

    #이미 위에서 감지해서 알아서 바꿈, 그래도 혹시 몰라서 소스코드는 남겨둠
    #bid 0 변경
    for zero in [y for y, x in enumerate(bidsList) if x == 0]:
        log.warning(f"bid 0 발견! | {md5sList[zero]}")
        try:
            bidsList[zero] = dbR.fetch("SELECT beatmap_id FROM beatmaps WHERE beatmap_md5 = %s", [md5sList[zero]])["beatmap_id"]
        except:
            try:
                bidsList[zero] = dbR.fetch("SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s", [setID, verList[zero]])["id"]
            except:
                log.warning("0 | RealBid가 redstarDB + cheesegull에서 조회되지 않음! 스킵함")
                bidsList[zero] = 0
        for bi, b, m in zip(beatmap_info, bidsList, md5sList):
            if bi["BeatmapMD5"] == m:
                bi["BeatmapID"] = b

    #중복 bid 찾기
    dup = [item for item, cnt in Counter(bidsList).items() if cnt > 1]
    if len(dup) != 0:
        log.warning("bid 중복 있음!")
        for i in dup:
            #중복 bid list index위치 찾기
            for idx in [y for y, x in enumerate(bidsList) if x == i]:
                #중복 bid 수정
                try:
                    bidsList[idx] = dbR.fetch("SELECT beatmap_id FROM beatmaps WHERE beatmap_md5 = %s", [md5sList[idx]])["beatmap_id"]
                except:
                    try:
                        bidsList[idx] = dbC.fetch("SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s", [setID, verList[idx]])["id"]
                    except:
                        log.warning("0 | RealBid가 cheesegull에서 조회되지 않음! 스킵함")
                        bidsList[idx] = 0
                for bi, b, m in zip(beatmap_info, bidsList, md5sList):
                    if bi["BeatmapMD5"] == m:
                        bi["BeatmapID"] = b
        
        #[log.debug(i) for i in beatmap_info]

    if int(setID) > 0:
        first_bid = min([x for x in bidsList if x > 0])
    else:
        first_bid = min([x for x in bidsList]) #커스텀 비트맵셋일 경우

    if not moving:
        shutil.rmtree(f"{dataFolder}/dl/{setID}")

    if bID is not None:
        try:
            redstar = next((i for i in beatmap_info if i["BeatmapID"] == int(bID)))
        except:
            redstar = None
        try:
            cheesegull = requests.get(f"https://cheesegull.{osuServerDomain}/api/b/{bID}", headers=requestHeaders).json()
            if not cheesegull and cheesegull["ParentSetID"] != int(setID): cheesegull = None
        except:
            cheesegull = None
        try:
            cho = [b for b in Bancho if b["beatmap_id"] == bID]
            if not cho: cho = None
        except:
            cho = None
        return_result = {"RedstarOSU": redstar, "cheesegull": cheesegull, "Bancho": cho} if redstar and cheesegull and cho else None
    else:
        try:
            cheesegull = requests.get(f"https://cheesegull.{osuServerDomain}/api/s/{setID}", headers=requestHeaders).json() if cheesegull else None
        except:
            cheesegull = None
        return_result = {"RedstarOSU": [int(setID), first_bid, beatmap_info], "cheesegull": cheesegull, "Bancho": Bancho}

    if not omsDB:
        pass #TODO : osu_media_server 테이블에 beatmapsinfo 항목에 INSERT 문 코드 넣기 (beatmapsinfo.py 복사해서 모듈형태로 가져오게 하기)
    else:
        pass #TODO : UPDATE 문으로 넣기
    return return_result

def move_files(setID, rq_type):
        isOsuFile = False
        result = osu_file_read(setID, rq_type, moving=True)["RedstarOSU"]
        #필요한 파일만 각 폴더로 이동
        for item in result[2]:
            isOsuFile = True
            #아래 코드 에러 방지용 (폴더가 없으면 에러남)
            if not os.path.isdir(f"{dataFolder}/bg/{setID}") and rq_type == "bg":
                os.mkdir(f"{dataFolder}/bg/{setID}")
                log.info(f"{dataFolder}/bg/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"{dataFolder}/thumb/{setID}") and rq_type == "thumb":
                os.mkdir(f"{dataFolder}/thumb/{setID}")
                log.info(f"{dataFolder}/thumb/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"{dataFolder}/audio/{setID}") and rq_type == "audio":
                os.mkdir(f"{dataFolder}/audio/{setID}")
                log.info(f"{dataFolder}/audio/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"{dataFolder}/preview/{setID}") and rq_type == "preview":
                os.mkdir(f"{dataFolder}/preview/{setID}")
                log.info(f"{dataFolder}/preview/{setID} 폴더 생성 완료!")
            try:
                if not os.path.isdir(f"{dataFolder}/video/{setID}") and item["BeatmapVideo"] is not None and rq_type == "video":
                    os.mkdir(f"{dataFolder}/video/{setID}")
                    log.info(f"{dataFolder}/video/{setID} 폴더 생성 완료!")
            except:
                #log.warning(f"{item['BeatmapID']} bid no video")
                pass
            if not os.path.isdir(f"{dataFolder}/osu/{setID}") and not IS_YOU_HAVE_OSU_PRIVATE_SERVER and rq_type == "osu":
                os.mkdir(f"{dataFolder}/osu/{setID}")
                log.info(f"{dataFolder}/osu/{setID} 폴더 생성 완료!")

            #log.debug(item)

            #BeatmapSetID용 미리듣기 + BG (b.redstar.moe/preview?예정)
            if item["BeatmapID"] == result[1]:
                if rq_type == "bg":
                    try:
                        extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                        shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapBG']}", f"{dataFolder}/bg/{setID}/+{setID}{extension}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | BG 처리함")
                    except:
                        try:
                            log.error(f"{setID} 비트맵셋은 BG가 없음 | 윈도우 파일명 기준으로 첫 번째꺼로 복사해봄")
                            item2 = result[2][0]["BeatmapBG"]
                            extension = item2[-5:][item2[-5:].find("."):]
                            shutil.copy(f"{dataFolder}/dl/{setID}/{item2}", f"{dataFolder}/bg/{setID}/+{setID}{extension}")
                            log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | BG 처리함")
                        except:
                            log.error(f"{setID} 비트맵셋은 BG가 없음 | +noImage_+{setID}.jpg로 저장함")
                            shutil.copy(f"static/img/noImage.jpg", f"{dataFolder}/bg/{setID}/+noImage_+{setID}.jpg")

                if rq_type == "thumb":
                    try:
                        extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                        shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapBG']}", f"{dataFolder}/thumb/{setID}/+{setID}{extension}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | thumb 처리함")
                    except:
                        #1465772 셋에서 thumb 에러나서 만듦
                        try:
                            log.error(f"{setID} 비트맵셋은 thumb가 없음 | 윈도우 파일명 기준으로 첫 번째꺼로 복사해봄")
                            item2 = result[2][0]["BeatmapBG"]
                            extension = item2[-5:][item2[-5:].find("."):]
                            shutil.copy(f"{dataFolder}/dl/{setID}/{item2}", f"{dataFolder}/thumb/{setID}/+{setID}{extension}")
                            log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | thumb 처리함")
                        except:
                            log.error(f"{setID} 비트맵셋은 thumb가 없음 | +noImage_{setID}.jpg로 저장함")
                            shutil.copy(f"static/img/noImage.jpg", f"{dataFolder}/thumb/{setID}/+noImage_{setID}.jpg")

                if rq_type == "preview":
                    try:
                        shutil.copy(f"{dataFolder}/dl/{setID}/{item['AudioFilename']}", f"{dataFolder}/preview/{setID}/{item['AudioFilename']}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | {item['AudioFilename']} 처리함")
                    except:
                        try:
                            log.error(f"{setID} 비트맵셋은 preview가 없음 | 윈도우 파일명 기준으로 첫 번째꺼로 복사해봄")
                            item2 = result[2][0]["AudioFilename"]
                            shutil.copy(f"{dataFolder}/dl/{setID}/{item2}", f"{dataFolder}/preview/{setID}/{item2}")
                            log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | BG 처리함")
                        except:
                            shutil.copy(f"static/audio/noAudio.mp3", f"{dataFolder}/preview/{setID}/noAudio_{setID}.mp3")
                            log.error(f"{setID} 비트맵셋은 preview가 없음 | noAudio_{setID}.mp3로 저장하고, preview도 처리함")

            if rq_type == "bg":
                try:
                    extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapBG']}", f"{dataFolder}/bg/{setID}/{item['BeatmapID']}{extension}")
                    log.info(f"{item['BeatmapID']} 비트맵 | BG 처리함")
                except:
                    log.error(f"{item['BeatmapID']} 비트맵은 BG가 없음 | noImage_{item['BeatmapID']}.jpg로 저장함")
                    shutil.copy(f"static/img/noImage.jpg", f"{dataFolder}/bg/{setID}/noImage_{item['BeatmapID']}.jpg")

            if rq_type == "audio":
                try:
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['AudioFilename']}", f"{dataFolder}/audio/{setID}/{item['AudioFilename']}")
                    log.info(f"{item['BeatmapID']} 비트맵 | audio 처리함")
                except:
                    log.error(f"{item['BeatmapID']} 비트맵은 audio가 없음 | noAudio.mp3로 저장함")
                    shutil.copy(f"static/audio/noAudio.mp3", f"{dataFolder}/audio/{setID}/noAudio.mp3")

            if rq_type == "video":
                try:
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapVideo']}", f"{dataFolder}/video/{setID}/{item['BeatmapVideo']}")
                    log.info(f"{item['BeatmapID']} 비트맵은 video가 존재함!")
                except:
                    pass
            
            if not IS_YOU_HAVE_OSU_PRIVATE_SERVER and rq_type == "osu":
                shutil.copy(f"{dataFolder}/dl/{setID}/{item['beatmapName']}", f"{dataFolder}/osu/{setID}/{item['BeatmapID']}.osu")
                log.info(f"{item['BeatmapID']} 비트맵 | osu 처리함")

            #lets | read_osu
            if rq_type.startswith("read_osu"):
                bid = int(rq_type.replace("read_osu_", ""))
                if int(item['BeatmapID']) == bid:
                    log.info(rq_type)
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['beatmapName']}", f"{lets_beatmaps_Folder}/{bid}.osu")
                    log.info(f"{bid}.osu | lets에 넣음")
                    shutil.rmtree(f"{dataFolder}/dl/{setID}")
                    return 0

        if not isOsuFile:
            raise FileNotFoundError(f".osu 파일이 존재하지 않는것으로 보임! | [WinError 3] 지정된 경로를 찾을 수 없습니다: '{dataFolder}/{rq_type}/{setID}'")

        #osu_file_read() 함수에 인자값으로 True를 넣어서 dl/{setID} 가 삭제 되지 않으므로 여기서 폴더 삭제함
        shutil.rmtree(f"{dataFolder}/dl/{setID}")
        return result

def choUnavailable(setID):
    unavailable = False
    audio_unavailable = download_unavailable = storyboard = 0
    Bancho_data = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_APIKEY}&s={setID}").json()
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
def check(setID, rq_type, checkRenewFile=False):
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
                res = requests.get(link, headers=requestHeaders, timeout=3, stream=True)
                statusCode = res.status_code
                header_filename = res.headers.get('Content-Disposition')
            except requests.exceptions.ReadTimeout as e:
                log.warning(f"{link} Timeout! | e = {e}")
                statusCode = 504
            except Exception as e:
                statusCode = res.status_code if res.status_code != 200 else 500
                log.error(f"{statusCode} | {e} | 파일다운 기본 예외처리 | url = {link}")

            if statusCode == 200:
                # 파일 크기를 얻습니다.
                file_size = int(res.headers.get('Content-Length', 0))

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

                # WAV 파일 재생을 별도의 스레드에서 수행
                def play_finished_dl():
                    os.system(f"ffplay -nodisp -autoexit static/audio/match-confirm.mp3 > {'nul' if os.name == 'nt' else '/dev/null'} 2>&1")
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
        log.info(f"{get_osz_fullName(setID)} 존재함")

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
        except:
            Bancho_LastUpdate,  omsDB = (None, {"last_update": None, "update_lock": 0})
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
                if rankStatus == 4:
                    rankStatus = 0
            except:
                rankStatus = dbC.fetch(f"SELECT ranked_status FROM sets WHERE id = %s", [setID])["ranked_status"]
                log.info(f"파일 최신화 cheesegull DB 랭크상태 조회 완료 : {rankStatus}")
            if rankStatus <= 0:
                oszHash = calculate_md5.file(f"{dataFolder}/dl/{fullSongName}")
                log.debug(f"oszHash = {oszHash}")
                for i in url:
                    newOszHash = requests.get(i, headers=requestHeaders, timeout=5, stream=True)
                    if newOszHash.status_code == 200:
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

    if checkRenewFile:
        return []
    elif dlsc != 200:
        return dlsc
    else:
        try:
            return move_files(setID, rq_type)
        except Exception as e:
            return e
            
def crf(bsid, rq_type):
    #파일 최신화
    if rq_type == "osz":
        ck = check(bsid, rq_type, checkRenewFile=True)
        if type(ck) is not list:
            return ck
    else:
        pass

#######################################################################################################################################

def read_list(bsid=""):
    result = {}

    if bsid == "":
        osz_file_list = [file for file in os.listdir(f"{dataFolder}/dl/") if file.endswith(".osz")]
        result["osz"] = {"list": osz_file_list, "count": len(osz_file_list)}
    else:
        osz_file_list = [get_osz_fullName(bsid)]
        result["osz"] = {"list": osz_file_list, "count": len(osz_file_list)}

    bg_file_list = [file for file in os.listdir(f"{dataFolder}/bg/{bsid}")]
    result["bg"] = {"list": bg_file_list, "count": len(bg_file_list)}

    thumb_file_list = [file for file in os.listdir(f"{dataFolder}/thumb/{bsid}")]
    result["thumb"] = {"list": thumb_file_list, "count": len(thumb_file_list)}

    audio_file_list = [file for file in os.listdir(f"{dataFolder}/audio/{bsid}")]
    result["audio"] = {"list": audio_file_list, "count": len(audio_file_list)}

    preview_file_list = [file for file in os.listdir(f"{dataFolder}/preview/{bsid}")]
    result["preview"] = {"list": preview_file_list, "count": len(preview_file_list)}

    try:
        video_file_list = [file for file in os.listdir(f"{dataFolder}/video/{bsid}")]
        result["video"] = {"list": video_file_list, "count": len(video_file_list)}
    except:
        result["video"] = {"list": "NO FOLDER", "count": 0}

    try:
        osu_file_list = [file for file in os.listdir(f"{dataFolder}/osu/{bsid}")]
        result["osu"] = {"list": osu_file_list, "count": len(osu_file_list)}
    except:
        result["osu"] = {"list": "NO FOLDER", "count": 0}

    return result

def read_bg(id):
    if "+" in id:
        id = str(id).replace("+", "")

        #파일 최신화
        crf(id, rq_type="bg")

        #bg폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/bg/{id}"):
            #파일 다운로드시에 500 뜨면 500 코드로 반환 예정, 만약 우리서버 문제면 main.py 에서 503 코드로 반환
            ck = check(id, rq_type="bg")
            if type(ck) is not list:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/bg/{id}") if file.startswith("+")]
        try:
            print(file_list[0])
        except:
            log.error(f"bsid = {id} | BG print(file_list[0]) 에러")
            ck = check(id, rq_type="bg")
            if type(ck) is not list:
                return ck
            return read_bg(f"+{id}")
        return f"{dataFolder}/bg/{id}/{file_list[0]}"
    else:
        try:
            bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
        except:
            try:
                bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
                log.info("RedstarOSU DB에서 bsid 찾음")
            except:
                raise KeyError("Not Found bsid!")

        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #파일 최신화
        crf(bsid, rq_type="bg")

        #bg폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/bg/{bsid}"):
            ck = check(bsid, rq_type="bg")
            if type(ck) is not list:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/bg/{bsid}") if file.startswith(str(id))]
        file_list_v2 = [file for file in os.listdir(f"{dataFolder}/bg/{bsid}") if file.startswith("noImage_")]
        file_list = file_list_v2 if file_list_v2 else file_list
        try:
            print(file_list[0])
        except:
            log.error(f"bid = {id} | BG print(file_list[0]) 에러")
            ck = check(bsid, rq_type="bg")
            if type(ck) is not list:
                return ck
            return read_bg(id)
        return f"{dataFolder}/bg/{bsid}/{file_list[0]}"
    
def read_thumb(id):
    if "l.jpg" in id:
        bsid = id.replace("l.jpg", "")
        img_size = (160, 120)
    else:
        bsid = id.replace(".jpg", "")
        img_size = (80, 60)

    #파일 최신화
    crf(bsid, rq_type="thumb")

    if os.path.isfile(f"{dataFolder}/thumb/{bsid}/{id}"):
        return f"{dataFolder}/thumb/{bsid}/{id}"
    elif os.path.isfile(f"{dataFolder}/thumb/{bsid}/noImage_{id}"):
        return f"{dataFolder}/thumb/{bsid}/noImage_{id}"
    else:
        #thumb폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/thumb/{bsid}"):
            ck = check(bsid, rq_type="thumb")
            if type(ck) is not list:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/thumb/{bsid}") if file.startswith("+")]
        try:
            print(file_list[0])
            if file_list[0].endswith(f"+noImage_{bsid}.jpg"):
                os.replace(f"{dataFolder}/thumb/{bsid}/{file_list[0]}", f"{dataFolder}/thumb/{bsid}/noImage_{id}")
                return f"{dataFolder}/thumb/{bsid}/noImage_{id}"
        except:
            log.error(f"bsid = {bsid} | thumb print(file_list[0]) 에러")
            ck = check(bsid, rq_type="thumb")
            if type(ck) is not list:
                return ck
            return read_thumb(id)

        img = Image.open(f"{dataFolder}/thumb/{bsid}/{file_list[0]}")
        # 이미지 모드를 RGBA에서 RGB로 변환
        img = img.convert("RGB")

        width, height = img.size
        if width / height == 4 / 3:
            log.info(f"이미 4:3 비율이라서 {img_size} 로만 자름")
            img.resize(img_size, Image.LANCZOS).save(f"{dataFolder}/thumb/{bsid}/{id}", quality=100)
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
            img_resize = img_cropped.resize(img_size, Image.LANCZOS)
            img_resize.save(f"{dataFolder}/thumb/{bsid}/{id}", quality=100)

        os.remove(f"{dataFolder}/thumb/{bsid}/{file_list[0]}")
        return f"{dataFolder}/thumb/{bsid}/{id}"

#osu_file_read() 역할 분할하기 (각각 따로 두기)
def read_audio(id, m=None):
    #ffmpeg -i "audio.ogg" -acodec libmp3lame -q:a 0 -y "audio.mp3"
    def audioSpeed(m, setID, file_list):
        #변환 시작 + 에러시 코덱 확인후 재 변환
        Codec = mediainfo(f"{dataFolder}/audio/{setID}/{file_list[0]}")["codec_name"]
        if Codec != "mp3":
            log.error(f"{file_list[0]} 코텍은 mp3가 아님 | {Codec}")

        try:
            m = int(m)
            if m == mods.DOUBLETIME: m = "DT"
            elif m == mods.NIGHTCORE or m == 576: m = "NC"
            elif m == mods.HALFTIME: m = "HT"
        except:
            m = m.upper() if m else None

        if m == "DT" and not "noAudio" in file_list[0]:
            log.chat("DT 감지")
            DTFilename = f"{dataFolder}/audio/{setID}/{file_list[0][:-4]}-DT.mp3" if not file_list[0].endswith("-DT.mp3") else f"{dataFolder}/audio/{setID}/{file_list[0]}"
            if os.path.isfile(DTFilename):
                return DTFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/audio/{setID}/{file_list[0]}" -af atempo=1.5 -acodec libmp3lame -q:a 0 -y "{DTFilename}"'
                log.chat(f"DT ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return DTFilename
        elif m == "NC" and not "noAudio" in file_list[0]:
            log.chat("NC 감지")
            NCFilename = f"{dataFolder}/audio/{setID}/{file_list[0][:-4]}-NC.mp3" if not file_list[0].endswith("-NC.mp3") else f"{dataFolder}/audio/{setID}/{file_list[0]}"
            if os.path.isfile(NCFilename):
                return NCFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/audio/{setID}/{file_list[0]}" -af asetrate={int(mediainfo(f"{dataFolder}/audio/{setID}/{file_list[0]}")["sample_rate"])}*1.5 -acodec libmp3lame -q:a 0 -y "{NCFilename}"'
                
                log.chat(f"NC ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return NCFilename
        elif m == "HT" and not "noAudio" in file_list[0]:
            log.chat("HT 감지")
            HTFilename = f"{dataFolder}/audio/{setID}/{file_list[0][:-4]}-HT.mp3" if not file_list[0].endswith("-HT.mp3") else f"{dataFolder}/audio/{setID}/{file_list[0]}"
            if os.path.isfile(HTFilename):
                return HTFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/audio/{setID}/{file_list[0]}" -af atempo=0.75 -acodec libmp3lame -q:a 0 -y "{HTFilename}"'
                log.chat(f"HT ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return HTFilename
        elif m == "PREVIEW" and not "noAudio" in file_list[0]:
            log.chat("preview 감지")
            PreviewFilename = f"{dataFolder}/audio/{setID}/{file_list[0][:-4]}-preview.mp3" if not file_list[0].endswith("-preview.mp3") else f"{dataFolder}/audio/{setID}/{file_list[0]}"
            if os.path.isfile(PreviewFilename):
                return PreviewFilename
            else:
                j = osu_file_read(setID, rq_type="preview")["RedstarOSU"]
                for i in j[2]:
                    if j[1] == i["BeatmapID"]:
                        prti = int(i["PreviewTime"])
                        if prti == -1:
                            audio = float(mediainfo(f"{dataFolder}/audio/{setID}/{file_list[0]}")["duration"])
                            PreviewTime = audio / 2.5
                            log.warning(f"{setID}.mp3 ({file_list[0]}) 의 PreviewTime 값이 {prti} 이므로 TotalLength / 2.5 == {PreviewTime} 로 세팅함")
                        else:
                            PreviewTime = prti / 1000

                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/audio/{setID}/{file_list[0]}" -ss {PreviewTime} -acodec libmp3lame -q:a 0 -y "{PreviewFilename}"'
                log.chat(f"preview ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return PreviewFilename
        else:
            return f"{dataFolder}/audio/{setID}/{file_list[0]}"

    if "+" in id:
        id = str(id).replace("+", "")

        #파일 최신화
        crf(id, rq_type="audio")

        #audio폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/audio/{id}"):
            ck = check(id, rq_type="audio")
            if type(ck) is not list:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/audio/{id}")]

        if len(file_list) > 1:
            AF = osu_file_read(id, rq_type="audio")["RedstarOSU"]
            for i in AF[2]:
                if AF[1] == i["BeatmapID"]:
                    file_list = [i['AudioFilename']]

        try:
            if not os.path.isfile(f"{dataFolder}/audio/{id}/{file_list[0]}") and os.path.isfile(f"{dataFolder}/audio/{id}/noAudio.mp3"):
                log.error(f"{id} bid 실제론 음악파일 없어보이며, noAudio.mp3가 폴더내에 존재함")
                file_list = ["noAudio.mp3"]
            print(file_list[0])
        except:
            log.error(f"bsid = {id} | audio print(file_list[0]) 에러")
            ck = check(id, rq_type="audio")
            if type(ck) is not list:
                return ck
            return read_audio(f"+{id}", m)

        return audioSpeed(m, id, file_list)
    else:
        #파일 최신화
        crf(id, rq_type="audio")

        try:
            bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
        except:
            try:
                bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
                log.info("RedstarOSU DB에서 bsid 찾음")
            except:
                raise KeyError("Not Found bsid!")

        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #audio폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/audio/{bsid}"):
            ck = check(bsid, rq_type="audio")
            if type(ck) is not list:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/audio/{bsid}")]

        if len(file_list) > 1:
            AF = osu_file_read(bsid, rq_type="audio")["RedstarOSU"]
            for i in AF[2]:
                if int(id) == i["BeatmapID"]:
                    file_list = [i['AudioFilename']]

        try:
            print(file_list[0])
            if not os.path.isfile(f"{dataFolder}/audio/{bsid}/{file_list[0]}") and os.path.isfile(f"{dataFolder}/audio/{bsid}/noAudio.mp3"):
                log.error(f"{id} bid 실제론 음악파일 없어보이며, noAudio.mp3가 폴더내에 존재함")
                file_list = ["noAudio.mp3"]
        except:
            log.error(f"bid = {id} | audio print(file_list[0]) 에러")
            ck = check(bsid, rq_type="audio")
            if type(ck) is not list:
                return ck
            return read_audio(id, m)

        return audioSpeed(m, bsid, file_list)

def read_preview(id):
    #source_{bsid}.mp3 먼저 확인시키기 ㄴㄴ audio에서 가져오기
    setID = id.replace(".mp3", "")

    #파일 최신화
    crf(setID, rq_type="preview")

    if not os.path.isfile(f"{dataFolder}/preview/{setID}/{id}"):
        if os.path.isfile(f"{dataFolder}/preview/{setID}/noAudio_{id}"):
            #위에서 오디오 없어서 이미 처리댐 (noAudio_{setID}.mp3)
            log.warning(f"noAudio_{id}")
            return f"{dataFolder}/preview/{setID}/noAudio_{id}"
        else:
            ck = check(setID, rq_type="preview")
            if type(ck) is not list:
                return ck
        
        if os.path.isfile(f"{dataFolder}/preview/{setID}/noAudio_{id}"):
            #위에서 오디오 없어서 이미 처리댐 (noAudio_{setID}.mp3)
            log.warning(f"noAudio_{id}")
            return f"{dataFolder}/preview/{setID}/noAudio_{id}"

        #음원 하이라이트 가져오기, 밀리초라서 / 1000 함
        PreviewTime = -1
        AudioFilename = ""
        j = osu_file_read(setID, rq_type="preview")["RedstarOSU"]
        
        for i in j[2]:
            if j[1] == i["BeatmapID"]:
                prti = int(i["PreviewTime"])
                AudioFilename = i["AudioFilename"]
                if prti == -1:
                    audio = float(mediainfo(f"{dataFolder}/preview/{setID}/{AudioFilename}")["duration"])
                    PreviewTime = audio / 2.5
                    log.warning(f"{setID}.mp3 ({AudioFilename}) 의 PreviewTime 값이 {prti} 이므로 TotalLength / 2.5 == {PreviewTime} 로 세팅함")
                else:
                    PreviewTime = prti / 1000

        if AudioFilename.endswith(".mp3"):
            ffmpeg_msg = f'ffmpeg -i "{dataFolder}/preview/{setID}/{AudioFilename}" -ss {PreviewTime} -t 30.821 -acodec copy -y "{dataFolder}/preview/{setID}/{id}"'
        else:
            ffmpeg_msg = f'ffmpeg -i "{dataFolder}/preview/{setID}/{AudioFilename}" -ss {PreviewTime} -t 30.821 -acodec libmp3lame -q:a 0 -y "{dataFolder}/preview/{setID}/{id}"'
            log.warning(f"ffmpeg_msg = {ffmpeg_msg}")
        
        log.chat(f"ffmpeg_msg = {ffmpeg_msg}")
        #변환 시작 + 에러시 코덱 확인후 재 변환
        if os.system(ffmpeg_msg) != 0:
            Codec = mediainfo(f"{dataFolder}/preview/{setID}/{AudioFilename}")["codec_name"]
            log.error(f"ffmpeg .mp3 변환 실패! | 코덱 조회: {Codec}")
            if Codec != "mp3":
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/preview/{setID}/{AudioFilename}" -ss {PreviewTime} -t 30.821 -acodec libmp3lame -q:a 0 -y "{dataFolder}/preview/{setID}/{id}"'
                if os.system(ffmpeg_msg) != 0:
                    log.error(f"{setID} | {AudioFilename} 변환 실패!")

        os.remove(f"{dataFolder}/preview/{setID}/{AudioFilename}")
    return f"{dataFolder}/preview/{setID}/{id}"

def read_video(id):
    try:
        bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    #파일 최신화
    crf(bsid, rq_type="video")

    #video폴더 파일 체크
    if not os.path.isdir(f"{dataFolder}/video/{bsid}"):
        ck = check(bsid, rq_type="video")
        if type(ck) is not list:
            return ck

    hasVideo = next((i["BeatmapVideo"] for i in osu_file_read(bsid, rq_type="video")["RedstarOSU"][2] if int(id) == i["BeatmapID"]), None)
    if hasVideo is None:
        log.warning(f"{id} 해당 비트맵은 .osu 파일에 비디오 정보가 없습니다!")
        try:
            #hasVideo = dbC.fetch("SELECT has_video FROM sets WHERE id = %s", [bsid])["has_video"]
            #반초로 조회함
            hasVideo = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_APIKEY}&b={id}", headers=requestHeaders)
            hasVideo = int(hasVideo.json()[0]["video"])

            if hasVideo != 0:
                file_list = [file for file in os.listdir(f"{dataFolder}/video/{bsid}") if file.endswith(".mp4")]
                if len(file_list) > 1:
                    AF = osu_file_read(bsid, rq_type="video")["RedstarOSU"]
                    for i in AF[2]:
                        if int(id) == i["BeatmapID"]:
                            file_list = [i['AudioFilename']]
                try:
                    #log.debug(print(file_list[0]))
                    print(file_list[0])
                except:
                    log.error(f"bid = {id} | video print(file_list[0]) 에러")
                    ck = check(bsid, rq_type="video")
                    if type(ck) is not list:
                        return ck
                    return read_video(id)
                return f"{dataFolder}/video/{bsid}/{file_list[0]}"
            else:
                raise
        except:
            return f"{id} Beatmap has no video!"
    else:
        #임시로 try 박아둠, 나중에 반초라던지 비디오 있나 요청하는거로 바꾸기
        if os.path.isfile(f"{dataFolder}/video/{bsid}/{hasVideo}"):
            return f"{dataFolder}/video/{bsid}/{hasVideo}"
            

def read_osz(id):
    #파일 최신화
    crf(id, rq_type="osz")

    filename = get_osz_fullName(id)
    if filename != f"{id} .osz" and os.path.isfile(f"{dataFolder}/dl/{filename}"):
        return {"path": f"{dataFolder}/dl/{filename}", "filename": filename}
    else:
        ck = check(id, rq_type="osz")
        if type(ck) is not list:
            return ck
        newFilename = get_osz_fullName(id)
        if os.path.isfile(f"{dataFolder}/dl/{newFilename}"):
            return {"path": f"{dataFolder}/dl/{newFilename}", "filename": newFilename}
        else:
            return 0

def read_osz_b(id):
    try:
        bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
    return read_osz(bsid)

def read_osu(id):
    try:
        bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

    #파일 최신화
    crf(bsid, rq_type=f"read_osu_{id}")

    sql = '''
        SELECT CONCAT(s.artist, ' - ', s.title, ' (', s.creator, ') [', b.diff_name, ']' '.osu') AS filename
        FROM sets AS s
        JOIN beatmaps AS b ON s.id = b.parent_set_id
        WHERE b.id = %s
    '''
    filename = dbC.fetch(sql, [id])
    log.debug(filename)

    #B:\redstar\lets\.data\beatmaps 우선시함
    if IS_YOU_HAVE_OSU_PRIVATE_SERVER and os.path.isfile(f"{lets_beatmaps_Folder}/{id}.osu"):
        log.info(f"{id}.osu 파일을 {lets_beatmaps_Folder}/{id}.osu에서 먼저 찾아서 반환함")
        if filename is None:
            log.error(f"filename is None | sql = {sql}")
            return None
        return {"path": f"{lets_beatmaps_Folder}/{id}.osu", "filename": filename["filename"]}
    else:
        if os.path.isfile(f"{dataFolder}/osu/{bsid}/{id}.osu"):
            if filename is None:
                log.error(f"filename is None | sql = {sql}")
                return None
            return {"path": f"{dataFolder}/osu/{bsid}/{id}.osu", "filename": filename["filename"]}
        else:
            ck = check(bsid, rq_type=f"osu")
            if type(ck) is not list:
                return ck
            return read_osu(id)

def filename_to_GetCheesegullDB(filename):
    try:
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
        log.error("osu filename에서 artist, title, creator, version 추출중 에러")

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
    result = filename_to_GetCheesegullDB(filename)
    log.debug(f"result = {result}")
    if result is None:
        #Bancho에 이름으로 bid 찾는 방법 찾아내기
        return None
    bid = result["id"]
    return read_osu(bid)

def read_covers(id, cover_type):
    if not os.path.isfile(f"{dataFolder}/covers/{id}/{cover_type}"):
        try:
            result = requests.get(f"https://assets.ppy.sh/beatmaps/{id}/covers/{cover_type}", headers=requestHeaders)
            if result.status_code == 200:
                with open(f"{dataFolder}/covers/{id}/{cover_type}", "wb") as file:
                    file.write(result.content)
                return f"{dataFolder}/covers/{id}/{cover_type}"
            else:
                return result.status_code
        except Exception as e:
            log.error(f"{id}, {cover_type} | covers 처리중 에러발생!")
            log.error(e)
            return 503
    else:
        return f"{dataFolder}/covers/{id}/{cover_type}"

def removeAllFiles(bsid):
    osz = get_osz_fullName(bsid)

    isdelosz = 0
    isdelbg = 0
    isdelthumb = 0
    isdelaudio = 0
    isdelpreview = 0
    isdelvideo = 0
    isdelosu = 0
    print("")

    #osz
    if osz == 0:
        log.error(f"{bsid} osz는 존재하지 않음")
    else:
        try:
            os.remove(f"{dataFolder}/dl/{osz}")
            log.info(f'파일 {osz} 가 삭제되었습니다.')
            isdelosz = 1
        except OSError as e:
            log.error(f'파일 삭제 실패: {e}')
    try:
        shutil.rmtree(f"{dataFolder}/dl/{bsid}")
        log.info(f'폴더 {dataFolder}/dl/{bsid} 가 삭제되었습니다.')
    except:
        pass

    #bg
    try:
        shutil.rmtree(f"{dataFolder}/bg/{bsid}")
        log.info(f'폴더 {dataFolder}/bg/{bsid} 가 삭제되었습니다.')
        isdelbg = 1
    except:
        pass

    #thumb
    try:
        shutil.rmtree(f"{dataFolder}/thumb/{bsid}")
        log.info(f'폴더 {dataFolder}/thumb/{bsid} 가 삭제되었습니다.')
        isdelthumb = 1
    except:
        pass

    #audio
    try:
        shutil.rmtree(f"{dataFolder}/audio/{bsid}")
        log.info(f'폴더 {dataFolder}/audio/{bsid} 가 삭제되었습니다.')
        isdelaudio = 1
    except:
        pass

    #preview
    try:
        shutil.rmtree(f"{dataFolder}/preview/{bsid}")
        log.info(f'폴더 {dataFolder}/preview/{bsid} 가 삭제되었습니다.')
        isdelpreview = 1
    except:
        pass

    #video
    try:
        shutil.rmtree(f"{dataFolder}/video/{bsid}")
        log.info(f'폴더 {dataFolder}/video/{bsid} 가 삭제되었습니다.')
        isdelvideo = 1
    except:
        pass

    #osu
    try:
        shutil.rmtree(f"{dataFolder}/osu/{bsid}")
        log.info(f'폴더 {dataFolder}/osu/{bsid} 가 삭제되었습니다.')
        isdelosu = 1
    except:
        pass
    isdelosu = 0

    return {"message": {0: "Doesn't exist", 1: "Delete success"} , "osz": isdelosz, "bg": isdelbg, "thumb": isdelthumb, "audio": isdelaudio, "preview": isdelpreview, "video": isdelvideo, "osu": isdelosu}

#dbR.close()
#dbC.close()