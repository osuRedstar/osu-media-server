import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        real_ip, request_url, country_code, client_ip, request_ip, request_CC, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server = getRequestInfo(self)
        data = {
            "code": 200,
            "oszCount": read_list()["osz"]["count"] if not request_ip and not request_CC else None,
            "oszSize": get_dir_size(f"{dataFolder}/dl") if not request_ip and not request_CC else None,
            "filesSize": get_dir_size(f"{dataFolder}/Songs") if not request_ip and not request_CC else None,
            "requestTime": round(time.time()),
            "request": {
                "IP": real_ip,
                "country": country_code,
                "X-Request-IP": request_ip,
                "X-Request-Country": request_CC,
                "User-Agent": User_Agent,
                "url": request_url,
                "Referer": Referer,
                "IsCloudflare": IsCloudflare,
                "IsNginx": IsNginx,
                "IsHttp": IsHttp,
                "Server": Server,
                "IsBlocked": True if rm != 200 else False,
                "ping": resPingMs(self)
            }
        }

        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
        self.write(json.dumps(data, indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))