import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            file = read_thumb(id)
            if file == 404:
                return send404(self, "bsid", id)
            elif file == 500:
                return send500(self, "bsid", id)
            elif file == 504:
                return send504(self, "bsid", id)
            elif type(file) == FileNotFoundError:
                raise file
            else:
                if file.endswith(f"noImage_{id}"):
                    self.set_status(404)
                IDM(self, file)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))