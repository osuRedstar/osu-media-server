import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback

class handler(tornado.web.RequestHandler):
    def get(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        u = self.get_argument("u", None)
        h = self.get_argument("h", None)
        vv = self.get_argument("vv", None)
        log.info(f"username : {u} | pwhash : {h} | vv : {vv}")
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
                self.set_header("return-fileinfo", json.dumps({"filename": path["filename"], "path": path["path"], "fileMd5": calculate_md5.file(path["path"])}))
                self.set_header('Content-Type', pathToContentType(path["path"])["Content-Type"])
                IDM(self, path["path"])
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))