import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200: return send403(self, rm)
        u = self.get_argument("u", None)
        h = self.get_argument("h", None)
        vv = self.get_argument("vv", None)
        log.info(f"username : {u} | pwhash : {h} | vv : {vv}")
        self.set_header("user-info", json.dumps({"u": u, "h": h, "vv": vv}))
        try:
            file = read_osz(id, u, h, vv)
            if file == 404: return send404(self, "bsid", id)
            elif file == 500: return send500(self, "bsid", id)
            elif file == 504: return send504(self, "bsid", id)
            elif type(file) == FileNotFoundError: raise file
            elif file == 0: self.write("ERROR")
            else: IDM(self, file)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally: self.set_header("Ping", str(resPingMs(self)))