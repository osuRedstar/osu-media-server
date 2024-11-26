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
            file = read_osz_b(id)
            if file == 404:
                return send404(self, "bid", id)
            elif file == 500:
                return send500(self, "bid", id)
            elif file == 504:
                return send504(self, "bid", id)
            elif type(file) == FileNotFoundError:
                raise file
            elif file == 0:
                self.write("ERROR")
            else:
                IDM(self, file)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))