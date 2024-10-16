import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self, bsid, bid):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            info = osu_file_read(bsid, rq_type="all", bID=bid, cheesegull=True, filesinfo=True)
            if info == 404:
                return send404(self, "bid", bid)
            elif info == 500:
                return send500(self, "bid", bid)
            elif info == 504:
                return send504(self, "bid", bid)
            elif type(info) == FileNotFoundError:
                raise info
            elif info is None:
                self.set_status(404)
                self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
                self.write(json.dumps({"code": 404, "message": "NODATA! Check bsid & bid"}, indent=2, ensure_ascii=False))
            else:
                info = json.dumps(info, indent=2, ensure_ascii=False)
                self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
                self.write(info)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", bid)
        finally:
            self.set_header("Ping", str(resPingMs(self)))