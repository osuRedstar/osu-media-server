import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback

class handler(tornado.web.RequestHandler):
    def get(self, bsid):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            info = osu_file_read(bsid, rq_type="all", cheesegull=True, filesinfo=True)
            if info == 404:
                return send404(self, "bsid", bsid)
            elif info == 500:
                return send500(self, "bsid", bsid)
            elif info == 504:
                return send504(self, "bsid", bsid)
            elif type(info) == FileNotFoundError:
                raise info
            else:
                info = json.dumps(info, indent=2, ensure_ascii=False)
                self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
                self.write(info)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", bsid)
        finally:
            self.set_header("Ping", str(resPingMs(self)))