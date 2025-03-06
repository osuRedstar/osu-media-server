import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self):
        rm = request_msg(self, botpass=True)
        if rm != 200: pass
        ip = self.get_argument("ip", None)
        country = self.get_argument("country", None)
        url = self.get_argument("url", None)
        user_agent = self.get_argument("user-agent", None)
        referer = self.get_argument("referer", None)
        botType = self.get_argument("type", None)
        count = self.get_argument("count", None)
        last_seen = self.get_argument("last_seen", None)
        data = findBot(ip, country, url, user_agent, referer, botType, count, last_seen)
        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
        self.write(json.dumps(data, indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))