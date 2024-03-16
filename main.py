import os
import config
import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
import geoip2.database
import time
import subprocess

conf = config.config("config.ini")

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
    self.set_header("return-fileinfo", json.dumps({"filename": "404.html", "path": "templates/404.html", "fileMd5": calculate_md5("templates/404.html")}))
    self.render("templates/404.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

def send500(self, inputType, input):
    self.set_status(500)
    self.set_header("return-fileinfo", json.dumps({"filename": "500.html", "path": "templates/500.html", "fileMd5": calculate_md5("templates/500.html")}))
    self.render("templates/500.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

def send503(self, e, inputType, input):
    self.set_status(503)
    #Exception = json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False)
    self.set_header("Exception", json.dumps({"type": str(type(e)), "error": str(e)}))
    self.set_header("return-fileinfo", json.dumps({"filename": "503.html", "path": "templates/503.html", "fileMd5": calculate_md5("templates/503.html")}))
    self.render("templates/503.html", inputType=inputType, input=input, Exception=json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False))
    self.set_header("Ping", str(resPingMs(self)))

def send504(self, inputType, input):
    #cloudflare 504 페이지로 연결됨
    self.set_status(504)
    self.set_header("return-fileinfo", json.dumps({"filename": "504.html", "path": "templates/504.html", "fileMd5": calculate_md5("templates/504.html")}))
    self.render("templates/504.html", inputType=inputType, input=input)
    self.set_header("Ping", str(resPingMs(self)))

####################################################################################################

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "index.html", "path": "templates/index.html", "fileMd5": calculate_md5("templates/index.html")}))
        self.render("templates/index.html")
        self.set_header("Ping", str(resPingMs(self)))

class ListHandler(tornado.web.RequestHandler):
    def get(self, bsid=""):
        log.chat(f"bsid = {bsid}")
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(read_list(bsid), indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))

class BgHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        if "+" in id:
            idType = "bsid"
        else:
            idType = "bid"
        try:
            file = read_bg(id)
            if file == 404:
                return send404(self, idType, id)
            elif file == 500:
                return send500(self, idType, id)
            elif file == 504:
                return send504(self, idType, id)
            elif type(file) == FileNotFoundError:
                raise file
            else: 
                self.set_header("return-fileinfo", json.dumps({"filename": id, "path": file, "fileMd5": calculate_md5(file)}))
                self.set_header('Content-Type', 'image/jpeg')
                with open(file, 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, idType, id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class ThumbHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            file = read_thumb(id)
            if file == 404:
                return send404(self, "bsid", id)
            elif file == 500:
                return send500(self, "bsid", id)
            elif file == 504:
                return send504(self, "bsid", id)
            elif type(file) == FileNotFoundError:
                raise file
            else:
                self.set_header("return-fileinfo", json.dumps({"filename": id, "path": file, "fileMd5": calculate_md5(file)}))
                self.set_header('Content-Type', 'image/jpeg')
                with open(file, 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class PreviewHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            file = read_preview(id)
            if file == 404:
                return send404(self, "bsid", id)
            elif file == 500:
                return send500(self, "bsid", id)
            elif file == 504:
                return send504(self, "bsid", id)
            elif type(file) == FileNotFoundError:
                raise file
            else:
                self.set_header("return-fileinfo", json.dumps({"filename": id, "path": file, "fileMd5": calculate_md5(file)}))
                self.set_header('Content-Type', 'audio/mp3')
                with open(file, 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class AudioHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        if "+" in id:
            idType = "bsid"
        else:
            idType = "bid"
        try:
            file = read_audio(id)
            if file == 404:
                return send404(self, idType, id)
            elif file == 500:
                return send500(self, idType, id)
            elif file == 504:
                return send504(self, idType, id)
            elif type(file) == FileNotFoundError:
                raise file
            else:
                self.set_header("return-fileinfo", json.dumps({"filename": id, "path": file, "fileMd5": calculate_md5(file)}))
                self.set_header('Content-Type', 'audio/mp3')
                with open(file, 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, idType, id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class VideoHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            readed_read_video = read_video(id)
            if readed_read_video == 404:
                return send404(self, "bid", id)
            elif readed_read_video == 500:
                return send500(self, "bid", id)
            elif readed_read_video == 504:
                return send504(self, "bid", id)
            elif type(readed_read_video) == FileNotFoundError:
                raise readed_read_video
            elif readed_read_video.endswith(".mp4"):
                self.set_header("return-fileinfo", json.dumps({"filename": id, "path": readed_read_video, "fileMd5": calculate_md5(readed_read_video)}))
                self.set_header('Content-Type', 'video/mp4')
                with open(readed_read_video, 'rb') as f:
                    self.write(f.read())
            else:
                self.set_status(404)
                self.set_header("return-fileinfo", json.dumps({"filename": id, "path": readed_read_video, "fileMd5": calculate_md5(readed_read_video)}))
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps({"code": 404, "message": "Sorry Beatmap has no videos", "funcmsg": readed_read_video}, indent=2, ensure_ascii=False))
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class OszHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        u = self.get_argument("u", None)
        h = self.get_argument("h", None)
        vv = self.get_argument("vv", None)
        log.info(f"username : {u} | pwhash? : {h} | vv : {vv}")
        self.set_header("user-info", json.dumps({"u": u, "h": h, "vv": vv}))

        try:
            path = read_osz(id)
            if path == 404:
                return send404(self, "bsid", id)
            elif path == 500:
                return send500(self, "bsid", id)
            elif path == 504:
                return send504(self, "bsid", id)
            elif type(path) == FileNotFoundError:
                raise path
            elif path == 0:
                self.write("ERROR")
            else:
                self.set_header("return-fileinfo", json.dumps({"filename": path["filename"], "path": path["path"], "fileMd5": calculate_md5(path["path"])}))
                self.set_header('Content-Type', 'application/x-osu-beatmap-archive')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class OszBHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            path = read_osz_b(id)
            if path == 404:
                return send404(self, "bid", id)
            elif path == 500:
                return send500(self, "bid", id)
            elif path == 504:
                return send504(self, "bid", id)
            elif type(path) == FileNotFoundError:
                raise path
            elif path == 0:
                self.write("ERROR")
            else:
                self.set_header("return-fileinfo", json.dumps({"filename": path["filename"], "path": path["path"], "fileMd5": calculate_md5(path["path"])}))
                self.set_header('Content-Type', 'application/x-osu-beatmap-archive')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class OsuHandler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            path = read_osu(id)
            if path == 404:
                return send404(self, "bid", id)
            elif path == 500:
                return send500(self, "bid", id)
            elif path == 504:
                return send504(self, "bid", id)
            elif type(path) == FileNotFoundError:
                raise path
            else:
                self.set_header("return-fileinfo", json.dumps({"filename": path["filename"], "path": path["path"], "fileMd5": calculate_md5(path["path"])}))
                self.set_header('Content-Type', 'application/x-osu-beatmap')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "favicon.ico", "path": "static/img/favicon.ico", "fileMd5": calculate_md5("static/img/favicon.ico")}))
        self.set_header('Content-Type', 'image/x-icon')
        with open("static/img/favicon.ico", 'rb') as f:
            self.write(f.read())
        self.set_header("Ping", str(resPingMs(self)))

class StaticHandler(tornado.web.RequestHandler):
    def get(self, item):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": item, "path": f"static/{item}", "fileMd5": calculate_md5(f"static/{item}")}))
        with open(f"static/{item}", 'rb') as f:
                self.write(f.read())
        self.set_header("Ping", str(resPingMs(self)))

class robots_txt(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "robots.txt", "path": "robots.txt", "fileMd5": calculate_md5("robots.txt")}))
        self.set_header("Content-Type", "text/plain")
        with open("robots.txt", 'rb') as f:
            self.write(f.read())
        self.set_header("Ping", str(resPingMs(self)))

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        real_ip, request_url, country_code, client_ip, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server = getRequestInfo(self)
        data = {
            "code": 200,
            "oszCount": read_list()["osz"]["count"],
            "requestTime": round(time.time()),
            "request": {
                "IP": real_ip,
                "country": country_code,
                "url": request_url,
                "User-Agent": User_Agent,
                "Referer": Referer,
                "IsCloudflare": IsCloudflare,
                "IsNginx": IsNginx,
                "IsHttp": IsHttp,
                "Server": Server,
                "ping": resPingMs(self)
                }
            }

        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data, indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))

class webMapsHandler(tornado.web.RequestHandler):
    def get(self, filename):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            path = read_osu_filename(filename)
            if path == 404:
                return send404(self, "filename", id)
            elif path == 500:
                return send500(self, "filename", id)
            elif path == 504:
                return send504(self, "filename", id)
            elif type(path) == FileNotFoundError:
                raise path
            elif path is None:
                self.set_status(204)
                return None
            else:
                self.set_header("return-fileinfo", json.dumps({"filename": path["filename"], "path": path["path"], "fileMd5": calculate_md5(path["path"])}))
                self.set_header('Content-Type', 'application/x-osu-beatmap')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "filename", filename)
        finally:
            self.set_header("Ping", str(resPingMs(self)))

class searchHandler(tornado.web.RequestHandler):
    def get(self, q):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        log.debug(self.request.uri)
        self.set_header("return-fileinfo", json.dumps({"filename": "mirror.html", "path": "templates/mirror.html", "fileMd5": calculate_md5("templates/mirror.html")}))
        self.render("templates/mirror.html", cheesegullUrlParam=self.request.uri)
        self.set_header("Ping", str(resPingMs(self)))

class removeHandler(tornado.web.RequestHandler):
    def get(self, bsid):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        key = self.get_argument("key", None)
        try:
            key2 = int(self.request.headers["BeatmapSetID"])
        except:
            key2 = None

        if key is None:
            send401(self, "Not Found key")
        elif key != "Debian":
            send401(self, f"{key} is Wrong key")
        elif key2 is None:
            send401(self, "Not Found key2")
        elif key2 != int(bsid):
            send401(self, f"{key2} is Wrong key2")
        else:
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(removeAllFiles(bsid), indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))

class filesinfoHandler(tornado.web.RequestHandler):
    def get(self, bsid):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(osu_file_read(bsid, rq_type="all", cheesegull=True), indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))

class filesinfoHandler2(tornado.web.RequestHandler):
    def get(self, bsid, bid):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)
        
        info = json.dumps(osu_file_read(bsid, rq_type="all", bID=bid, cheesegull=True), indent=2, ensure_ascii=False)
        if info is not None:
            self.set_header("Content-Type", "application/json")
            self.write(info)
            self.set_header("Ping", str(resPingMs(self)))
        else:
            self.set_status(404)
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({"code": 404, "message": "NODATA! Check bsid & bid"}, indent=2, ensure_ascii=False))
            self.set_header("Ping", str(resPingMs(self)))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/list", ListHandler),
        (r"/list/([^/]+)", ListHandler),
        (r"/bg/([^/]+)", BgHandler),
        (r"/thumb/([^/]+)", ThumbHandler),
        (r"/preview/([^/]+)", PreviewHandler),
        (r"/audio/([^/]+)", AudioHandler),
        (r"/video/([^/]+)", VideoHandler),
        (r"/d/([^/]+)", OszHandler),
        (r"/b/([^/]+)", OszBHandler),
        (r"/osu/([^/]+)", OsuHandler),
        (r"/favicon.ico", FaviconHandler),
        (r"/static/(.*)", StaticHandler),
        #(r"/favicon.ico", tornado.web.StaticFileHandler, {"path": "static/img/favicon.ico"})
        #(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r"/robots.txt", robots_txt),
        (r"/status", StatusHandler),
        (r"/web/maps/(.*)", webMapsHandler),
        (r"/search(.*)", searchHandler),
        (r"/remove/([^/]+)", removeHandler),
        (r"/filesinfo/([^/]+)", filesinfoHandler),
        (r"/filesinfo/([^/]+)/([^/]+)", filesinfoHandler2),
    ])

if __name__ == "__main__":
    folder_check()
    if conf.config["server"]["flaskdebug"] == "0":
        debugMode = False
    else:
        debugMode = True
    app = make_app()
    port = int(conf.config["server"]["port"])
    app.listen(port)
    log.info(f"Server Listen on http://localhost:{port} Port | OS = {'Windows' if os.name == 'nt' else 'UNIX'}")
    tornado.ioloop.IOLoop.current().start()