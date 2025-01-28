import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
import struct
import datetime
import io
from helpers import requestsManager
from functions import readableMods, getAcc

MODULE_NAME = "replayParserHandler"
class handler(requestsManager.asyncRequestHandler):
    """
    Handler for /replayparser

    """
    def asyncGet(self): self.render("../templates/replayParser.html")

    def asyncPost(self):
        dl = True if type(self.get_argument("dl", default=False)) != bool else False
        try:
            scoreDataEnc = self.request.files["score"][0]["body"]
            log.info(f'Parsing Replay File!{" For Download File" if dl else ""} | {self.request.files["score"][0]["filename"]}')

            def dotTicksToUnix(dotnet_ticks):
                timestamp = datetime.datetime(1, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=dotnet_ticks/10)
                return int(timestamp.timestamp())

            def readULEB128(data):
                result = shift = 0
                while True:
                    byte = data.read(1)
                    if not byte: raise ValueError("Unexpected end of data while reading ULEB128")
                    byte = ord(byte); result |= (byte & 0x7F) << shift; shift += 7
                    if not byte & 0x80: break
                return result

            def unpackString(data):
                indicator = data.read(1)
                if indicator == b"\x00": return ""
                elif indicator == b"\x0b": return data.read(readULEB128(data)).decode('utf-8')
                else: raise ValueError("Invalid string indicator")

            def unpackReplayData(data):
                data = io.BytesIO(data) #BytesIO 객체 생성
                play_mode = struct.unpack("<B", data.read(1))[0]
                version = struct.unpack("<I", data.read(4))[0]
                beatmap_md5 = unpackString(data)
                username = unpackString(data)
                replay_md5 = unpackString(data)
                count_300 = struct.unpack("<H", data.read(2))[0]
                count_100 = struct.unpack("<H", data.read(2))[0]
                count_50 = struct.unpack("<H", data.read(2))[0]
                gekis_count = struct.unpack("<H", data.read(2))[0]
                katus_count = struct.unpack("<H", data.read(2))[0]
                misses_count = struct.unpack("<H", data.read(2))[0]
                score = struct.unpack("<I", data.read(4))[0]
                max_combo = struct.unpack("<H", data.read(2))[0]
                full_combo = struct.unpack("<B", data.read(1))[0]
                mods = struct.unpack("<I", data.read(4))[0]
                life_bar_graph = unpackString(data)
                time = dotTicksToUnix(struct.unpack("<Q", data.read(8))[0])
                rawReplay = data.read(struct.unpack("<I", data.read(4))[0])
                id = struct.unpack("<Q", data.read(8))[0]

                if dl: return rawReplay
                acc = getAcc(play_mode, count_300, count_100, count_50, gekis_count, katus_count, misses_count)
                bid = dbR.fetch("SELECT beatmap_id, beatmapset_id FROM beatmaps WHERE beatmap_md5 = %s", [beatmap_md5]); bsid = bid["beatmapset_id"]; bid = bid["beatmap_id"]
                bname = next((d["beatmapName"] for d in osu_file_read(bsid, rq_type="all", cheesegull=True, filesinfo=True)["RedstarOSU"][2] if beatmap_md5 == d["BeatmapMD5"]), None)
                osz = get_osz_fullName(bsid).replace(".osz", "")
                if bid:
                    cmd = f'oppai\\oppai.exe "{dataFolder}\\Songs\\{osz}\\{bname}" {acc}% -m1 +{readableMods(mods)} {max_combo}x {misses_count}xm -m{play_mode} -ojson'
                    with os.popen(cmd) as c: pp = json.loads(c.buffer.read().decode("utf-8"))
                else: pp = None
                return json.dumps(
                    {
                        "dlLink": "https://" + self.request.host + self.request.uri + "?dl",
                        "id": id,
                        "play_mode": play_mode,
                        "version": version,
                        "beatmap_md5": beatmap_md5,
                        "username": username,
                        "replay_md5": replay_md5,
                        "300_count": count_300,
                        "100_count": count_100,
                        "50_count": count_50,
                        "gekis_count": gekis_count,
                        "katus_count": katus_count,
                        "misses_count": misses_count,
                        "score": score,
                        "max_combo": max_combo,
                        "full_combo": full_combo,
                        "mods": mods,
                        "life_bar_graph": life_bar_graph,
                        "time": time,
                        "acc": acc,
                        "oppai": pp,
                        "rawReplay": str(rawReplay)
                    }, indent=2, ensure_ascii=False
                )
            scoreData = unpackReplayData(scoreDataEnc)
        except: exceptionE()
        finally:
            if dl: self.set_header('Content-Type', self.request.files["score"][0]["content_type"]); self.write(scoreData)
            else: self.set_header("Content-Type", pathToContentType(".json")["Content-Type"]); self.write(scoreData)