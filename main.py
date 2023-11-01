import os
import config
import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import read_list, read_bg, read_thumb, read_audio, read_preview, read_video, read_osz, read_osz_b, read_osu, folder_check, read_osu_filename
import json

conf = config.config("config.ini")

def request_msg(self):
    # Logging the request IP address
    print("")
    try:
        real_ip = self.request.headers["Cf-Connecting-Ip"]
        request_uri = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
        country_code = self.request.headers["Cf-Ipcountry"]
    except:
        log.warning("cloudflare를 거치지 않아서 country_code 조회가 안댐, real_ip는 nginx header에서 가져옴")
        try:
            real_ip = self.request.headers["X-Real-Ip"]
            request_uri = self.request.headers["X-Forwarded-Proto"] + "://" + self.request.host + self.request.uri
            country_code = "XX"
        except:
            log.warning("http로 접속시도함 | cloudflare를 거치지 않아서 country_code 조회가 안댐, real_ip는 http요청이라서 바로 뜸")
            real_ip = self.request.remote_ip
            request_uri = self.request.protocol + "://" + self.request.host + self.request.uri
            country_code = "XX"
    client_ip = self.request.remote_ip
    try:
        User_Agent = self.request.headers["User-Agent"]
    except:
        log.error("User-Agent 값이 존재하지 않음!")
        User_Agent = ""
    log.info(f"Request from IP: {real_ip}, {client_ip} ({country_code}) | URL: {request_uri} | From: {User_Agent}")

def send404(self, inputType, input):
    self.set_status(404)
    self.set_header("return-filename", json.dumps({"filename": "404.html", "path": "templates/404.html"}))
    self.render("templates/404.html", inputType=inputType, input=input)

def send500(self, inputType, input):
    self.set_status(500)
    self.set_header("return-filename", json.dumps({"filename": "500.html", "path": "templates/500.html"}))
    self.render("templates/500.html", inputType=inputType, input=input)

def send503(self, inputType, input):
    self.set_status(503)
    self.set_header("return-filename", json.dumps({"filename": "503.html", "path": "templates/503.html"}))
    self.render("templates/503.html", inputType=inputType, input=input)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.set_header("return-filename", json.dumps({"filename": "index.html", "path": "templates/index.html"}))
        self.render("templates/index.html")

class ListHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.set_header("return-filename", json.dumps({"filename": "", "path": ""}))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(read_list(), indent=4))

class BgHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            file = read_bg(id)
            if file == 500:
                return send500(self, file["inputType"], id)
            elif file == 404:
                return send404(self, file["inputType"], id)
            else: 
                self.set_header("return-filename", json.dumps({"filename": id, "path": file["path"]}))
                self.set_header('Content-Type', 'image/jpeg')
                with open(file["path"], 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, file["inputType"], id)

class ThumbHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            file = read_thumb(id)
            if file == 500:
                return send500(self,"bsid", id)
            elif file == 404:
                return send404(self, "bsid", id)
            else:
                self.set_header("return-filename", json.dumps({"filename": id, "path": file}))
                self.set_header('Content-Type', 'image/jpeg')
                with open(file, 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, "bsid", id)

class PreviewHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            file = read_preview(id)
            if file == 500:
                return send500(self, "bsid", id)
            elif file == 404:
                return send404(self, "bsid", id)
            else:
                self.set_header("return-filename", json.dumps({"filename": id, "path": file}))
                self.set_header('Content-Type', 'audio/mp3')
                with open(file, 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, "bsid", id)

class AudioHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            file = read_audio(id)
            if file == 500:
                return send500(self, file["inputType"], id)
            elif file == 404:
                return send404(self, file["inputType"], id)
            else:
                self.set_header("return-filename", json.dumps({"filename": id, "path": file["path"]}))
                self.set_header('Content-Type', 'audio/mp3')
                with open(file["path"], 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, file["inputType"], id)

class VideoHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            readed_read_video = read_video(id)
            if readed_read_video == 500:
                return send500(self, "bid", id)
            elif readed_read_video == 404:
                return send404(self, "bid", id)
            elif readed_read_video.endswith(".mp4"):
                self.set_header("return-filename", json.dumps({"filename": id, "path": readed_read_video}))
                self.set_header('Content-Type', 'video/mp4')
                with open(readed_read_video, 'rb') as f:
                    self.write(f.read())
            else:
                self.set_status(404)
                self.set_header("return-filename", json.dumps({"filename": id, "path": readed_read_video}))
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps({"code": 404, "message": "Sorry Beatmap has no videos", "funcmsg": readed_read_video}, indent=4))
        except:
            return send503(self, "bid", id)

class OszHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            path = read_osz(id)
            if path == 500:
                return send500(self, "bsid", id)
            elif path == 404:
                return send404(self, "bsid", id)
            elif path == 0:
                self.write("ERROR")
            else:
                self.set_header("return-filename", json.dumps({"filename": path["filename"], "path": path["path"]}))
                self.set_header('Content-Type', 'application/x-osu-beatmap-archive')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, "bsid", id)

class OszBHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            path = read_osz_b(id)
            if path == 500:
                return send500(self, "bid", id)
            elif path == 404:
                return send404(self, "bid", id)
            elif path == 0:
                self.write("ERROR")
            else:
                self.set_header("return-filename", json.dumps({"filename": path["filename"], "path": path["path"]}))
                self.set_header('Content-Type', 'application/x-osu-beatmap-archive')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, "bid", id)

class OsuHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        try:
            path = read_osu(id)
            if path == 500:
                return send500(self, "bid", id)
            elif path == 404:
                return send404(self, "bid", id)
            else:
                self.set_header("return-filename", json.dumps({"filename": path["filename"], "path": path["path"]}))
                self.set_header('Content-Type', 'application/x-osu-beatmap')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, "bid", id)

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.set_header("return-filename", json.dumps({"filename": "favicon.png", "path": "static/img/favicon.png"}))
        self.set_header('Content-Type', 'image/png')
        with open("static/img/favicon.png", 'rb') as f:
            self.write(f.read())

class StaticHandler(tornado.web.RequestHandler):
    def get(self, item):
        request_msg(self)
        self.set_header("return-filename", json.dumps({"filename": item, "path": f"static/{item}"}))
        with open(f"static/{item}", 'rb') as f:
                self.write(f.read())

class robots_txt(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.set_header("return-filename", json.dumps({"filename": "robots.txt", "path": "robots.txt"}))
        self.set_header("Content-Type", "text/plain")
        with open("robots.txt", 'rb') as f:
            self.write(f.read())

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.set_header("return-filename", json.dumps({"filename": "", "path": ""}))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"code": 200, "oszCount": read_list()["osz"]["count"]}, indent=4))

class webMapsHandler(tornado.web.RequestHandler):
    def get(self, filename):
        request_msg(self)
        try:
            path = read_osu_filename(filename)
            if path == 500:
                return send500(self, "filename", filename)
            elif path == 404:
                return send404(self, "filename", filename)
            elif path is None:
                return None
            else:
                self.set_header("return-filename", json.dumps({"filename": path["filename"], "path": path["path"]}))
                self.set_header('Content-Type', 'application/x-osu-beatmap')
                self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
                with open(path['path'], 'rb') as f:
                    self.write(f.read())
        except:
            return send503(self, "filename", filename)

class searchHandler(tornado.web.RequestHandler):
    def get(self, q):
        request_msg(self)
        log.debug(self.request.uri)
        self.set_header("return-filename", json.dumps({"filename": "mirror.html", "path": "templates/mirror.html"}))
        self.render("templates/mirror.html", cheesegullUrlParam=self.request.uri)

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
        (r"/robots.txt", robots_txt),
        (r"/status", StatusHandler),
        (r"/web/maps/(.*)", webMapsHandler),
        (r"/search(.*)", searchHandler),
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
