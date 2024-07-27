import tornado.ioloop
import tornado.web
import lets_common_log.logUtils as log
from functions import *
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

class handler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, folder, file):
        rm = request_msg(self, botpass=False)
        if rm != 200:
            return send403(self, rm)

        try:
            file = yield executor.submit(read_raw, folder, file)
            if file: IDM(self, file)
            else: self.set_status(404)
        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bid", id)
        finally:
            self.set_header("Ping", str(resPingMs(self)))