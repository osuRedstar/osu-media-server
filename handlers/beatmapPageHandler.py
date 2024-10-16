import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, id):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            bid = check(id, rq_type="all")[1]
            if bid == 404:
                return send404(self, "bsid", id)
            elif bid == 500:
                return send500(self, "bsid", id)
            elif bid == 504:
                return send504(self, "bsid", id)
            elif type(bid) == FileNotFoundError:
                raise bid
            elif bid == 0:
                self.write("ERROR")
            else:
                self.redirect(f"https://{osuServerDomain}/b/{bid}")
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))