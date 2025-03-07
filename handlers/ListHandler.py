import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, bsid=""):
        rm = request_msg(self, botpass=False)
        if rm != 200: return send403(self, rm)
        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
        self.write(json.dumps(read_list(bsid), indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))