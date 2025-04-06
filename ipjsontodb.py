from helpers import logUtils as log
from helpers import dbConnector
import os
import time
from helpers import config
import json
import traceback

st = time.time()

def exceptionE(msg=""): e = traceback.format_exc(); log.error(f"{msg} \n{e}"); return e

dbO = dbConnector.db("osu_media_server")

with open("IPs.json", "r") as f: ips = json.load(f)
for i in ips:
    values = (None,) + tuple(i.values()) + (1,)
    sql = f"INSERT INTO ips VALUES ({', '.join(['%s'] * len(values))})"
    log.warning(dbO.mogrify(sql, values))
    dbO.execute(sql, values)

log.chat(f"{round(time.time() - st, 2)} sec")