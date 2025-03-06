import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self):
        rm = request_msg(self, botpass=True)
        if rm != 200: pass
        try:
            q = self.get_argument("q", 0)
            ptct = pathToContentType(q)
            self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
            if ptct: self.write(json.dumps({"status": 200, "msg": ptct}, indent=2, ensure_ascii=False))
            else: self.set_status(400); self.write(json.dumps({"status": 400, "msg": "q param required!"}, indent=2, ensure_ascii=False))
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally: self.set_header("Ping", str(resPingMs(self)))