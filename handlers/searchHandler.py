import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback

class handler(tornado.web.RequestHandler):
    def get(self, q):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        log.debug(self.request.uri)
        self.set_header("return-fileinfo", json.dumps({"filename": "mirror.html", "path": "templates/mirror.html", "fileMd5": calculate_md5("templates/mirror.html")}))
        self.render("templates/mirror.html", cheesegullUrlParam=self.request.uri)
        self.set_header("Ping", str(resPingMs(self)))