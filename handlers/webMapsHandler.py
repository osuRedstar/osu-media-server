import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, filename):
        rm = request_msg(self, botpass=False)
        if rm != 200: return send403(self, rm)
        try:
            file = read_osu_filename(filename)
            if file == 404: return send404(self, "filename", id)
            elif file == 500: return send500(self, "filename", id)
            elif file == 504: return send504(self, "filename", id)
            elif type(file) == FileNotFoundError: raise file
            elif file is None: self.set_status(204); return None
            else: IDM(self, file)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "filename", filename)
        finally: self.set_header("Ping", str(resPingMs(self)))