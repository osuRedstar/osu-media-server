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

        ip = self.get_argument("ip", None)
        country = self.get_argument("country", None)
        url = self.get_argument("url", None)
        user_agent = self.get_argument("user-agent", None)
        referer = self.get_argument("referer", None)
        botType = self.get_argument("type", None)
        count = self.get_argument("count", None)
        last_seen = self.get_argument("last_seen", None)

        with open("IPs.json", "r") as f: bots = json.load(f)
        data = [] #필터링
        for entry in bots:
            if ((ip is None or ip in entry.get("IP")) and
                (country is None or country in entry.get("Country")) and
                (url is None or url in entry.get("URL")) and
                (user_agent is None or user_agent in entry.get("User-Agent")) and
                (referer is None or referer in entry.get("Referer")) and
                (botType is None or botType in entry.get("Type")) and
                (count is None or entry.get("Count") == int(count)) and
                (last_seen is None or entry.get("Last_seen") == int(last_seen))):
                data.append(entry)

        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
        self.write(json.dumps(data, indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))