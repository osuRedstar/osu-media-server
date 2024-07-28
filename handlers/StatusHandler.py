import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback

class handler(tornado.web.RequestHandler):
    def get(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        real_ip, request_url, country_code, client_ip, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server = getRequestInfo(self)
        data = {
            "code": 200,
            "oszCount": read_list()["osz"]["count"],
            "oszSize": get_dir_size(f"{dataFolder}/dl"),
            "filesSize": get_dir_size(f"{dataFolder}/Songs"),
            "requestTime": round(time.time()),
            "request": {
                "IP": real_ip,
                "country": country_code,
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