import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import config
from helpers import requestsManager

conf = config.config("config.ini")

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, bsid):
        rm = request_msg(self, botpass=False)
        if rm != 200: return send403(self, rm)
        key = self.get_argument("key", None)
        try: key2 = int(self.request.headers["BeatmapSetID"])
        except: key2 = None
        if key is None: send401(self, "Not Found key")
        elif key != conf.config["server"]["removekey"]: send401(self, f"{key} is Wrong key")
        elif key2 is None: send401(self, "Not Found key2")
        elif key2 != int(bsid): send401(self, f"{key2} is Wrong key2")
        else:
            self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
            self.write(json.dumps(removeAllFiles(bsid), indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))