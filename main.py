import os
import config
import tornado.ioloop
import tornado.web
from functions import *
import lets_common_log.logUtils as log
import json
import drpc
import getmmdb

#from handlers import MainHandler
from handlers import ListHandler
from handlers import BgHandler, BgHandler_async
from handlers import ThumbHandler, ThumbHandler_async
from handlers import PreviewHandler, PreviewHandler_async
from handlers import AudioHandler, AudioHandler_async
from handlers import VideoHandler, VideoHandler_async
from handlers import beatmapPageHandler, beatmapPageHandler_async
from handlers import OszHandler, OszHandler_async
from handlers import OszBHandler, OszBHandler_async
from handlers import OsuHandler, OsuHandler_async
from handlers import replayParserHandler
from handlers import readableModsHandler, readableModsReverseHandler
from handlers import rawHandler, rawHandler_async
from handlers import IPSelfHandler, IPHandler
#from handlers import FaviconHandler
#from handlers import StaticHandler
#from handlers import robots_txt
from handlers import StatusHandler
from handlers import webMapsHandler, webMapsHandler_async
from handlers import searchHandler
from handlers import removeHandler
from handlers import filesinfoHandler, filesinfoHandler_async
from handlers import filesinfoHandler2, filesinfoHandler2_async
from handlers import coversHandler

conf = config.config("config.ini")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200: pass

        self.set_header("return-fileinfo", json.dumps({"filename": "index.html", "path": "templates/index.html", "fileMd5": calculate_md5.file("templates/index.html")}))
        self.render("templates/index.html")
        self.set_header("Ping", str(resPingMs(self)))

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200: pass

        self.set_header("return-fileinfo", json.dumps({"filename": "favicon.ico", "path": "static/img/favicon.ico", "fileMd5": calculate_md5.file("static/img/favicon.ico")}))
        self.set_header('Content-Type', pathToContentType("static/img/favicon.ico")["Content-Type"])
        with open("static/img/favicon.ico", 'rb') as f: self.write(f.read())
        self.set_header("Ping", str(resPingMs(self)))

class StaticHandler(tornado.web.RequestHandler):
    def get(self, item):
        rm = request_msg(self, botpass=True)
        if rm != 200: pass

        self.set_header("return-fileinfo", json.dumps({"filename": item, "path": f"static/{item}", "fileMd5": calculate_md5.file(f"static/{item}")}))
        self.set_header("Content-Type", pathToContentType(item)["Content-Type"])
        with open(f"static/{item}", 'rb') as f: self.write(f.read())
        self.set_header("Ping", str(resPingMs(self)))

class robots_txt(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200: pass

        self.set_header("return-fileinfo", json.dumps({"filename": "robots.txt", "path": "robots.txt", "fileMd5": calculate_md5.file("robots.txt")}))
        self.set_header("Content-Type", pathToContentType("robots.txt")["Content-Type"])
        with open("robots.txt", 'rb') as f: self.write(f.read())
        self.set_header("Ping", str(resPingMs(self)))



def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/list", ListHandler.handler),
        (r"/list/([^/]+)", ListHandler.handler),
        (r"/status", StatusHandler.handler),
        (r"/search", searchHandler.handler),
        (r"/bg/([^/]+)", BgHandler.handler),
        (r"/thumb/([^/]+)", ThumbHandler.handler),
        (r"/preview/([^/]+)", PreviewHandler.handler),
        (r"/audio/([^/]+)", AudioHandler.handler),
        (r"/video/([^/]+)", VideoHandler.handler),
        (r"/s/([^/]+)", beatmapPageHandler.handler),
        (r"/d/([^/]+)", OszHandler.handler),
        (r"/b/([^/]+)", OszBHandler.handler),
        (r"/osu/([^/]+)", OsuHandler.handler),
        (r"/web/maps/(.*)", webMapsHandler.handler),
        (r"/remove/([^/]+)", removeHandler.handler),
        (r"/filesinfo/([^/]+)", filesinfoHandler.handler),
        (r"/filesinfo/([^/]+)/([^/]+)", filesinfoHandler2.handler),
        (r"/replayparser", replayParserHandler.handler),
        (r"/readableMods", readableModsHandler.handler),
        (r"/readableModsReverse", readableModsReverseHandler.handler),
        (r"/raw/([^/]+)/([^/]+)", rawHandler.handler),
        (r"/ip", IPSelfHandler.handler),
        (r"/ip/([^/]+)", IPHandler.handler),

        (r"/favicon.ico", FaviconHandler),
        (r"/static/(.*)", StaticHandler),
        #(r"/favicon.ico", tornado.web.StaticFileHandler, {"path": "static/img/favicon.ico"})
        #(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r"/robots.txt", robots_txt),

        #assets.ppy.sh
        (r"/beatmaps/([^/]+)/covers/([^/]+)", coversHandler.handler),
    ])

""" def make_app(): #async
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/list", ListHandler.handler),
        (r"/list/([^/]+)", ListHandler.handler),
        (r"/bg/([^/]+)", BgHandler_async.handler),
        (r"/thumb/([^/]+)", ThumbHandler_async.handler),
        (r"/preview/([^/]+)", PreviewHandler_async.handler),
        (r"/audio/([^/]+)", AudioHandler_async.handler),
        (r"/video/([^/]+)", VideoHandler_async.handler),
        (r"/s/([^/]+)", beatmapPageHandler.handler),
        (r"/d/([^/]+)", OszHandler_async.handler),
        (r"/b/([^/]+)", OszBHandler_async.handler),
        (r"/osu/([^/]+)", OsuHandler_async.handler),
        (r"/status", StatusHandler.handler),
        (r"/web/maps/(.*)", webMapsHandler.handler),
        (r"/search", searchHandler.handler),
        (r"/remove/([^/]+)", removeHandler.handler),
        (r"/filesinfo/([^/]+)", filesinfoHandler_async.handler),
        (r"/filesinfo/([^/]+)/([^/]+)", filesinfoHandler2_async.handler),
        (r"/replayparser", replayParserHandler.handler),
        (r"/readableMods", readableModsHandler.handler),
        (r"/readableModsReverse", readableModsReverseHandler.handler),
        (r"/raw/([^/]+)/([^/]+)", rawHandler.handler),
        (r"/ip", IPSelfHandler.handler),
        (r"/ip/([^/]+)", IPHandler.handler),

        (r"/favicon.ico", FaviconHandler),
        (r"/static/(.*)", StaticHandler),
        #(r"/favicon.ico", tornado.web.StaticFileHandler, {"path": "static/img/favicon.ico"})
        #(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
        (r"/robots.txt", robots_txt),

        #assets.ppy.sh
        (r"/beatmaps/([^/]+)/covers/([^/]+)", coversHandler.handler),
    ]) """

if __name__ == "__main__":
    getmmdb.dl()
    drpc.drpcStart()
    folder_check()
    #if conf.config["server"]["flaskdebug"] == "0": debugMode = False
    #else: debugMode = True
    app = make_app()
    port = int(conf.config["server"]["port"])
    app.listen(port)
    log.info(f"Server Listen on http://localhost:{port} Port | OS = {'Windows' if os.name == 'nt' else 'UNIX'}")
    tornado.ioloop.IOLoop.current().start()