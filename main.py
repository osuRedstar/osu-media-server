import os
import config
import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
import geoip2.database

conf = config.config("config.ini")

def request_msg(self, botpass=False):
    # Logging the request IP address
    print("")
    try:
        real_ip = self.request.headers["Cf-Connecting-Ip"]
        request_uri = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
        country_code = self.request.headers["Cf-Ipcountry"]
    except Exception as e:
        log.warning(f"cloudflare를 거치지 않음, real_ip는 nginx header에서 가져옴 | {e}")
        try:
            real_ip = self.request.headers["X-Real-Ip"]
            request_uri = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
        except Exception as e:
            log.warning(f"http로 접속시도함 | cloudflare를 거치지 않음, real_ip는 http요청이라서 바로 뜸 | {e}")
            real_ip = self.request.remote_ip
            request_uri = self.request.protocol + "://" + self.request.host + self.request.uri

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
        reader.close()

    client_ip = self.request.remote_ip
    try:
        User_Agent = self.request.headers["User-Agent"]
    except:
        User_Agent = ""
        log.error("User-Agent 값이 존재하지 않음!")

    def logmsg(msg):
        if botpass:
            log.warning(msg)
        else:
            log.error(msg)

    #필?터?링
    if "bot" in User_Agent.lower() and not "discord" in User_Agent.lower():
        logmsg(f"bot 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_uri} | From: {User_Agent}")
        return "bot"
    elif "python-requests" in User_Agent.lower():
        logmsg(f"python-requests 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_uri} | From: {User_Agent}")
        return "python-requests"
    elif "python-urllib" in User_Agent.lower():
        logmsg(f"Python-urllib 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_uri} | From: {User_Agent}")
        return "Python-urllib"
    elif User_Agent == "osu!":
        log.info(f"osu! 감지! | Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_uri} | From: {User_Agent}")
        return 200
    else:
        log.info(f"Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_uri} | From: {User_Agent}")
        return 200

def send401(self, errMsg):
    self.set_status(401)
    self.set_header("Content-Type", "application/json")
    self.write(json.dumps({"code": 401, "error": errMsg}, indent=2, ensure_ascii=False))

def send403(self, rm):
    self.set_status(403)
    self.set_header("Content-Type", "application/json")
    self.write(json.dumps({"code": 403, "error": f"{rm} is Not allowed!!", "message": "contect --> support@redstar.moe"}, indent=2, ensure_ascii=False))

def send404(self, inputType, input):
    self.set_status(404)
    self.set_header("return-fileinfo", json.dumps({"filename": "404.html", "path": "templates/404.html", "fileMd5": calculate_md5("templates/404.html")}))
    self.render("templates/404.html", inputType=inputType, input=input)

def send500(self, inputType, input):
    self.set_status(500)
    self.set_header("return-fileinfo", json.dumps({"filename": "500.html", "path": "templates/500.html", "fileMd5": calculate_md5("templates/500.html")}))
    self.render("templates/500.html", inputType=inputType, input=input)

def send503(self, e, inputType, input):
    self.set_status(503)
    #Exception = json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False)
    self.set_header("Exception", json.dumps({"type": str(type(e)), "error": str(e)}))
    self.set_header("return-fileinfo", json.dumps({"filename": "503.html", "path": "templates/503.html", "fileMd5": calculate_md5("templates/503.html")}))
    self.render("templates/503.html", inputType=inputType, input=input, Exception=json.dumps({"type": str(type(e)), "error": str(e)}, ensure_ascii=False))

def send504(self, inputType, input):
    #cloudflare 504 페이지로 연결됨
    self.set_status(504)
    self.set_header("return-fileinfo", json.dumps({"filename": "504.html", "path": "templates/504.html", "fileMd5": calculate_md5("templates/504.html")}))
    self.render("templates/504.html", inputType=inputType, input=input)

####################################################################################################

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "index.html", "path": "templates/index.html", "fileMd5": calculate_md5("templates/index.html")}))
        self.render("templates/index.html")

class ListHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(read_list(), indent=2, ensure_ascii=False))

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

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "favicon.ico", "path": "static/img/favicon.ico", "fileMd5": calculate_md5("static/img/favicon.ico")}))
        self.set_header('Content-Type', 'image/x-icon')
        with open("static/img/favicon.ico", 'rb') as f:
            self.write(f.read())

class StaticHandler(tornado.web.RequestHandler):
    def get(self, item):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": item, "path": f"static/{item}", "fileMd5": calculate_md5(f"static/{item}")}))
        with open(f"static/{item}", 'rb') as f:
                self.write(f.read())

class robots_txt(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "robots.txt", "path": "robots.txt", "fileMd5": calculate_md5("robots.txt")}))
        self.set_header("Content-Type", "text/plain")
        with open("robots.txt", 'rb') as f:
            self.write(f.read())

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"code": 200, "oszCount": read_list()["osz"]["count"]}, indent=2, ensure_ascii=False))

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

class searchHandler(tornado.web.RequestHandler):
    def get(self, q):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        log.debug(self.request.uri)
        self.set_header("return-fileinfo", json.dumps({"filename": "mirror.html", "path": "templates/mirror.html", "fileMd5": calculate_md5("templates/mirror.html")}))
        self.render("templates/mirror.html", cheesegullUrlParam=self.request.uri)

class removeHandler(tornado.web.RequestHandler):
    def get(self, bsid):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        key = self.get_argument("key", None)
        try:
            key2 = int(self.request.headers["BeatmapID"])
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

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/list", ListHandler),
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
    log.info(f"Server Listen on {port} Port")
    tornado.ioloop.IOLoop.current().start()
