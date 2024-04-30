import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
import config

conf = config.config("config.ini")
osuServerDomain = conf.config["server"]["osuServerDomain"]

class handler(tornado.web.RequestHandler):
    def get(self, id, cover_type):
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
                self.set_header("return-fileinfo", json.dumps({"filename": id, "path": file, "fileMd5": calculate_md5(file)}))
                self.set_header('Content-Type', pathToContentType(file)["Content-Type"])
                IDM(self, file)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))