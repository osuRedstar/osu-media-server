import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self):
        rm = request_msg(self, botpass=True)
        if rm != 200:
            pass

        data = IPtoFullData(getIP(self))
        log.info(f"{data['ip']} ({data['country']}) | IP 셀프조회 들어옴")

        self.set_header("return-fileinfo", json.dumps({"filename": "", "path": "", "fileMd5": ""}))
        self.set_header("Content-Type", pathToContentType(".json")["Content-Type"])
        self.write(json.dumps(data, indent=2, ensure_ascii=False))
        self.set_header("Ping", str(resPingMs(self)))