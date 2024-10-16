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
            readed_read_video = read_video(id)
            log.debug(readed_read_video)
            if readed_read_video == 404:
                return send404(self, "bid", id)
            elif readed_read_video == 500:
                return send500(self, "bid", id)
            elif readed_read_video == 504:
                return send504(self, "bid", id)
            elif type(readed_read_video) == FileNotFoundError:
                raise readed_read_video
            elif readed_read_video.startswith(dataFolder):
                IDM(self, readed_read_video)
            else:
                self.set_status(404)
                self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
                self.write(json.dumps({"code": 404, "message": "Sorry Beatmap has no videos", "funcmsg": readed_read_video}, indent=2, ensure_ascii=False))
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))