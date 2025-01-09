import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, folder, file):
        rm = request_msg(self, botpass=False)
        if rm != 200: return send403(self, rm)
        try:
            file = read_raw(folder, file)
            if file: IDM(self, file)
            else: self.set_status(404)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", id)
        finally: self.set_header("Ping", str(resPingMs(self)))