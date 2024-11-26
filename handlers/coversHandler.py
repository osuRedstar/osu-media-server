import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
from helpers import config
from helpers import requestsManager

conf = config.config("config.ini")
osuServerDomain = conf.config["server"]["osuServerDomain"]

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, id, cover_type):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        try:
            file = read_covers(id, cover_type)
            #covers용 sendXXX() 함수 만들기
            if file == 404:
                return self.set_status(404)
                return send404(self, "bsid", id)
            elif file == 500:
                return send500(self, "bsid", id)
            elif file == 504:
                return send504(self, "bsid", id)
            elif type(file) == FileNotFoundError:
                raise file
            else: 
                IDM(self, file)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))