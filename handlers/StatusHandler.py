import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self):
        try:
            isjson = int(self.get_argument("isjson", 1))
            isinfo = int(self.get_argument("isinfo", 1))
        except: isjson = isinfo = 1
        rm = request_msg(self, botpass=True)
        if rm != 200: pass
        real_ip, request_url, country_code, client_ip, User_Agent, Referer, IsCloudflare, IsNginx, IsHttp, Server = getRequestInfo(self)
        data = {
            "code": 200,
            "oszCount": read_list()["osz"]["count"] if isinfo else -1,
            "oszSize": get_dir_size(f"{dataFolder}/dl") if isinfo else -1,
            "filesSize": get_dir_size(f"{dataFolder}/Songs") if isinfo else -1,
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
        if isjson: self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
        self.write(json.dumps(data, indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))