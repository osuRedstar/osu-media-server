import os
import config
import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import read_list, read_bg, read_thumb, read_audio, read_preview, read_video, read_osz, read_osz_b, read_osu, folder_check, read_osu_filename

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

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.render("templates/index.html")

class ListHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.write(read_list())

class BgHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        self.set_header('Content-Type', 'image/jpeg')
        with open(read_bg(id), 'rb') as f:
            self.write(f.read())
        

class ThumbHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        self.set_header('Content-Type', 'image/jpeg')
        with open(read_thumb(id), 'rb') as f:
            self.write(f.read())

class PreviewHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        self.set_header('Content-Type', 'audio/mp3')
        with open(read_audio(id), 'rb') as f:
            self.write(f.read())

class AudioHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        self.set_header('Content-Type', 'audio/mpeg')
        with open(read_preview(id), 'rb') as f:
            self.write(f.read())

class VideoHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        readed_read_video = read_video(id)
        if readed_read_video.endswith(".mp4"):
            self.set_header('Content-Type', 'video/mp4')
            with open(readed_read_video, 'rb') as f:
                self.write(f.read())
        else:
            self.set_status(404)
            self.write({"code": 404, "message": "Sorry Beatmap has no videos", "funcmsg": readed_read_video})

class OszHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        path = read_osz(id)
        if path == 0:
            self.write("ERROR")
        else:
            self.set_header('Content-Type', 'application/x-osu-beatmap-archive')
            self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
            with open(path['path'], 'rb') as f:
                self.write(f.read())

class OszBHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        path = read_osz_b(id)
        if path == 0:
            self.write("ERROR")
        else:
            self.set_header('Content-Type', 'application/x-osu-beatmap-archive')
            self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
            with open(path['path'], 'rb') as f:
                self.write(f.read())

class OsuHandler(tornado.web.RequestHandler):
    def get(self, id):
        request_msg(self)
        path = read_osu(id)
        self.set_header('Content-Type', 'application/x-osu-beatmap')
        self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
        with open(path['path'], 'rb') as f:
            self.write(f.read())

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.set_header('Content-Type', 'image/png')
        with open("static/img/favicon.png", 'rb') as f:
            self.write(f.read())

class StaticHandler(tornado.web.RequestHandler):
    def get(self, item):
        request_msg(self)
        with open(f"static/{item}", 'rb') as f:
                self.write(f.read())

class robots_txt(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        with open("robots.txt", 'rb') as f:
                self.set_header("Content-Type", "text/plain")
                self.write(f.read())

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        request_msg(self)
        self.write({"code": 200, "oszCount": read_list()["osz"]["count"]})

class webMapsHandler(tornado.web.RequestHandler):
    def get(self, filename):
        request_msg(self)

        path = read_osu_filename(filename)
        if path is None:
            return None
        self.set_header('Content-Type', 'application/x-osu-beatmap')
        self.set_header('Content-Disposition', f'attachment; filename="{path["filename"]}"')
        with open(path['path'], 'rb') as f:
            self.write(f.read())

class searchHandler(tornado.web.RequestHandler):
    def get(self, q):
        request_msg(self)
        log.debug(self.request.uri)
        self.render("templates/mirror.html", cheesegullUrlParam=self.request.uri)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/list", ListHandler),
        (r"/bg/([^/]+)", BgHandler),
        (r"/thumb/([^/]+)", ThumbHandler),
        (r"/audio/([^/]+)", PreviewHandler),
        (r"/preview/([^/]+)", AudioHandler),
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
