import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
import struct
import datetime
import io



MODULE_NAME = "readableModsReverseHandler"
class handler(tornado.web.RequestHandler):
    """
    Handler for /readableModsReverse

    """
    def get(self):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        m = self.get_argument("m", default=None)
        try:
            mods = readableModsReverse(m)
            if type(mods) != int:
                raise Exception(mods)
            else:
                log.info(f"{m} --> {mods}")
                self.set_status(200)
                self.set_header('Content-Type', pathToContentType(".json")["Content-Type"])
                self.write(json.dumps({"code": 200, "request_mods": m, "mods": mods, "msg": None}, indent=2))
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")

            self.set_status(400)
            self.set_header('Content-Type', pathToContentType(".json")["Content-Type"])
            self.write(json.dumps({"code": 400, "request_mods": m, "mods": None, "msg": str(e)}, indent=2))
        finally:
            self.set_header("Ping", str(resPingMs(self)))