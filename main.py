import os
import config
import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json

#from handlers import MainHandler
from handlers import ListHandler
from handlers import BgHandler
from handlers import ThumbHandler
from handlers import PreviewHandler
from handlers import AudioHandler
from handlers import VideoHandler
from handlers import OszHandler
from handlers import OszBHandler
from handlers import OsuHandler
#from handlers import FaviconHandler
#from handlers import StaticHandler
#from handlers import robots_txt
from handlers import StatusHandler
from handlers import webMapsHandler
from handlers import searchHandler
from handlers import removeHandler
from handlers import filesinfoHandler
from handlers import filesinfoHandler2
from handlers import coversHandler

conf = config.config("config.ini")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        self.set_header("return-fileinfo", json.dumps({"filename": "index.html", "path": "templates/index.html", "fileMd5": calculate_md5("templates/index.html")}))
        self.render("templates/index.html")
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



def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/list", ListHandler.handler),
        (r"/list/([^/]+)", ListHandler.handler),
        (r"/bg/([^/]+)", BgHandler.handler),
        (r"/thumb/([^/]+)", ThumbHandler.handler),
        (r"/preview/([^/]+)", PreviewHandler.handler),
        (r"/audio/([^/]+)", AudioHandler.handler),
        (r"/video/([^/]+)", VideoHandler.handler),
        (r"/d/([^/]+)", OszHandler.handler),
        (r"/b/([^/]+)", OszBHandler.handler),
        (r"/osu/([^/]+)", OsuHandler.handler),

        (r"/favicon.ico", FaviconHandler),
        (r"/static/(.*)", StaticHandler),
        #(r"/favicon.ico", tornado.web.StaticFileHandler, {"path": "static/img/favicon.ico"})
        #(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r"/robots.txt", robots_txt),

        (r"/status", StatusHandler.handler),
        (r"/web/maps/(.*)", webMapsHandler.handler),
        (r"/search(.*)", searchHandler.handler),
        (r"/remove/([^/]+)", removeHandler.handler),
        (r"/filesinfo/([^/]+)", filesinfoHandler.handler),
        (r"/filesinfo/([^/]+)/([^/]+)", filesinfoHandler2.handler),

        #assets.ppy.sh
        (r"/beatmaps/([^/]+)/covers/([^/]+)", coversHandler.handler),
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