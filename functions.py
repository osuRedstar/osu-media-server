from lets_common_log import logUtils as log
from dbConnent import db
import zipfile
import os
import shutil
import requests
from tqdm import tqdm
import config
from PIL import Image
import hashlib
import re
from pydub import AudioSegment
from pydub.playback import play as PlaySound
import threading
import time
import json
from collections import Counter
import subprocess

dbR = db("redstar")
dbC = db("cheesegull")

#beatmap_md5
def calculate_md5(filename):
    md5 = hashlib.md5()
    with open(filename, "rb") as file:
        while True:
            data = file.read(8192)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

conf = config.config("config.ini")

OSU_APIKEY = conf.config["osu"]["osuApikey"]
#lets.py 형태의 사설서버를 소유중이면 lets\.data\beatmaps 에서만 .osu 파일을 가져옴
IS_YOU_HAVE_OSU_PRIVATE_SERVER = bool(conf.config["osu"]["IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py"])
lets_beatmaps_Folder = conf.config["osu"]["lets.py_beatmaps_Folder_Path"]
dataFolder = conf.config["server"]["dataFolder"]
oszRenewTime = int(conf.config["server"]["oszRenewTime"])
osuServerDomain = conf.config["server"]["osuServerDomain"]

requestHeaders = {"User-Agent": f"RedstarOSU's MediaServer (python requests) | https://b.{osuServerDomain}"}

#API 키 테스트
log.info("Bancho apikeyStatus check...")
apikeyStatus = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_APIKEY}&b=-1", headers=requestHeaders)
if apikeyStatus.status_code != 200:
    log.warning("[!] Bancho apikey does not work.")
    log.warning("[!] Please edit your config.ini and run the server again.")
    exit()
log.info("Done!")

#ffmpeg 설치확인
if os.system(f"ffmpeg -version > {'nul' if os.name == 'nt' else '/dev/null'} 2>&1") != 0:
    log.warning(f"ffmpeg Does Not Found!! | ignore? (y/n) ")
    if input("").lower() != "y":
        print("exit")
        if os.name != "nt":
            print("sudo apt install ffmpeg")
        else:
            print("https://github.com/BtbN/FFmpeg-Builds/releases")
        exit()
    else:
        print("ignored")
        log.warning("Maybe Not work preview & audio (DT, NC, HT)")

#ffprobe 설치확인
if os.system(f"ffprobe -version > {'nul' if os.name == 'nt' else '/dev/null'} 2>&1") != 0:
    log.warning(f"ffprobe Does Not Found!! | ignore? (y/n) ")
    if input("").lower() != "y":
        print("exit")
        if os.name != "nt":
            print("sudo apt install ffmpeg")
        else:
            print("https://github.com/BtbN/FFmpeg-Builds/releases")
        exit()
    else:
        print("ignored")
        log.warning("Maybe Not work check audio Codec")

def folder_check():
    if not os.path.isdir(dataFolder):
        os.mkdir(dataFolder)
        log.info(f"{dataFolder} 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/dl"):
        os.mkdir(f"{dataFolder}/dl")
        log.info(f"{dataFolder}/dl 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/dl-old"):
        os.mkdir(f"{dataFolder}/dl-old")
        log.info(f"{dataFolder}/dl-old 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/audio"):
        os.mkdir(f"{dataFolder}/audio")
        log.info(f"{dataFolder}/audio 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/preview"):
        os.mkdir(f"{dataFolder}/preview")
        log.info(f"{dataFolder}/preview 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/video"):
        os.mkdir(f"{dataFolder}/video")
        log.info(f"{dataFolder}/video 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/thumb"):
        os.mkdir(f"{dataFolder}/thumb")
        log.info(f"{dataFolder}/thumb 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/bg"):
        os.mkdir(f"{dataFolder}/bg")
        log.info(f"{dataFolder}/bg 폴더 생성")
    if not os.path.isdir(f"{dataFolder}/osu") and not IS_YOU_HAVE_OSU_PRIVATE_SERVER:
        os.mkdir(f"{dataFolder}/osu")
        log.info(f"{dataFolder}/osu 폴더 생성")

def get_osz_fullName(setID):
    try:
        fullName = [file for file in os.listdir(f"{dataFolder}/dl/") if file.startswith(f"{setID} ")][0]
        return fullName
    except:
        return 0

def osu_file_read(setID, rq_type, moving=False):
    #/filesinfo 조회시 osz 없을때 오류 방지
    if get_osz_fullName(setID) == 0 and rq_type == "all":
        ck = check(setID, rq_type)
        if ck is not None:
            return ck

    #압축파일에 문제생겼을 때 chimu에서 재 다운로드
    try:
        zipfile.ZipFile(f'{dataFolder}/dl/{get_osz_fullName(setID)}').extractall(f'{dataFolder}/dl/{setID}')
    except zipfile.BadZipFile as e:
        ck = check(setID, rq_type, site=1)
        if ck is not None:
            return ck
        try:
            zipfile.ZipFile(f'{dataFolder}/dl/{get_osz_fullName(setID)}').extractall(f'{dataFolder}/dl/{setID}')
        except zipfile.BadZipFile as e:
            log.error(f"압축파일 오류: {e}")
    
    file_list = os.listdir(f"{dataFolder}/dl/{setID}")
    file_list_osu = [file for file in file_list if file.endswith(".osu")]

    beatmap_info = []
    underV10 = False

    # readline_all.py
    for beatmapName in file_list_osu:
        log.info(beatmapName)
        temp = {}
        bg_ignore = False
        beatmap_md5 = calculate_md5(f"{dataFolder}/dl/{setID}/{beatmapName}")
        temp["BeatmapMD5"] = beatmap_md5

        with open(f"{dataFolder}/dl/{setID}/{beatmapName}", 'r', encoding="utf-8") as f:
            line = f.read()

            line = line[line.find("osu file format v"):]
            try:
                osu_file_format_version = int(line.split("\n")[0].replace("osu file format v", "").replace(" ", ""))
            except:
                osu_file_format_version = 0
            if osu_file_format_version == 0:
                log.error("osu file format v0")
            elif osu_file_format_version < 10:
                underV10 = True
                log.error(f"{setID} 비트맵셋의 어떤 비트맵은 시이이이이발 osu file format 이 10이하 ({osu_file_format_version}) 이네요? 시발련들아?")
                #틀딱곡 BeatmapID 를 Version 쪽에 넘김

            line = line[line.find("AudioFilename:"):]
            try:
                AudioFilename = line.split("\n")[0].replace("AudioFilename:", "")
                AudioFilename = AudioFilename.replace(" ", "", 1) if AudioFilename.startswith(" ") else AudioFilename
            except:
                AudioFilename = None

            line = line[line.find("PreviewTime:"):]
            try:
                PreviewTime = line.split("\n")[0].replace("PreviewTime:", "")
                PreviewTime = int(PreviewTime.replace(" ", "", 1) if PreviewTime.startswith(" ") else PreviewTime)
            except:
                PreviewTime = None
            
            line = line[line.find("Version:"):]
            try:
                Version = line.split("\n")[0].replace("Version:", "")
                Version = Version.replace(" ", "", 1) if Version.startswith(" ") else Version
            except:
                Version = None

            if osu_file_format_version >= 10:
                line = line[line.find("BeatmapID:"):]
                try:
                    BeatmapID = line.split("\n")[0].replace("BeatmapID:", "")
                    BeatmapID = int(BeatmapID.replace(" ", "", 1) if BeatmapID.startswith(" ") else BeatmapID)
                except:
                    BeatmapID = 0
            else:
                log.warning(f"osu file format v{osu_file_format_version} | files bid = 0")
                BeatmapID = 0

            line = line[line.find("//Background and Video events"):]
            try:
                if line.split("\n")[1].lower().startswith("video"):
                    BeatmapVideo = line.split("\n")[1]
                    BeatmapVideo = BeatmapVideo[BeatmapVideo.find('"') + 1 : BeatmapVideo.find('"', BeatmapVideo.find('"') + 1)]
                    BeatmapBG = line.split("\n")[2]
                else:
                    BeatmapVideo = None
                    BeatmapBG = line.split("\n")[1]
                BeatmapBG = BeatmapBG[BeatmapBG.find('"') + 1 : BeatmapBG.find('"', BeatmapBG.find('"') + 1)]
            except:
                BeatmapBG = None
                BeatmapVideo = None

            temp["osu_file_format_v"] = osu_file_format_version if osu_file_format_version != "" else None
            temp["AudioFilename"] = AudioFilename if AudioFilename != "" else None
            temp["PreviewTime"] = PreviewTime if PreviewTime != "" else None
            temp["Version"] = Version if Version != "" else None
            temp["BeatmapID"] = BeatmapID if BeatmapID != "" else None
            temp["BeatmapBG"] = BeatmapBG if BeatmapBG != "" else None
            temp["BeatmapVideo"] = BeatmapVideo if BeatmapVideo != "" else None
            temp["beatmapName"] = beatmapName if beatmapName != "" else None

            """ while True:
                line = f.readline()
                #간혹 확장자가 대문자인 경우가 있어서 전부 소문자로 변경함
                lineCheck = line.lower()
                if not line: break

                #ㅈ같은 osu file format < osu file format v10 은 거르쟈 시발련들아
                if "osu file format" in line:
                    osu_file_format_version = line.replace("osu file format v", "")

                    # BOM 문자 제거
                    if osu_file_format_version.startswith('\ufeff'):
                        osu_file_format_version = osu_file_format_version[1:]
                        log.warning("BOM 문자 제거")
                    osu_file_format_version = int(osu_file_format_version)
                    temp["osu_file_format_v"] = osu_file_format_version
                    if osu_file_format_version < 10:
                        underV10 = True
                        log.error(f"{setID} 비트맵셋의 어떤 비트맵은 시이이이이발 osu file format 이 10이하 ({osu_file_format_version}) 이네요? 시발련들아?")
                        #틀딱곡 BeatmapID 를 Version 쪽에 넘김

                if "BeatmapID:" in line and not underV10:
                    spaceFilter = line.replace("BeatmapID:", "").replace("\n", "")
                    if spaceFilter.startswith(" "):
                        spaceFilter = spaceFilter.replace(" ", "", 1)
                    temp["BeatmapID"] = int(spaceFilter)
                elif "Version:" in line:
                    spaceFilter = line.replace("Version:", "").replace("\n", "")
                    if spaceFilter.startswith(" "):
                        spaceFilter = spaceFilter.replace(" ", "", 1)
                    temp["Version"] = spaceFilter

                    #틀딱곡 BeatmapID 넘겨옴
                    if underV10:
                        # 정규식 패턴
                        pattern = r'\[([^\]]+)\]\.osu$'
                        match = re.search(pattern, beatmapName)
                        if match:
                            diffname = match.group(1)
                            sql = "SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s"
                            # windows 특수문자 이슈
                            if diffname != temp["Version"] and temp["Version"] != "":
                                log.error(f"diffname 매치 안됨! .osu안의 결과물 사용! | diffname = {diffname} | temp['Version'] = {temp['Version']}")
                                result = dbC.fetch(sql, [setID, temp["Version"]])
                            else:
                                result = dbC.fetch(sql, [setID, diffname])

                            if result is None:
                                return None
                            temp["BeatmapID"] = result["id"]

                        log.info(f"{setID} 틀딱곡 cheesegull db에서 조회완료")
                        log.warning(f"{setID}/{temp['BeatmapID']} 틀딱곡 BeatmapID 세팅 완료")
                elif "AudioFilename:" in line and (rq_type == "audio" or rq_type == "preview" or rq_type == "all"):
                    spaceFilter = line.replace("AudioFilename:", "").replace("\n", "")
                    if spaceFilter.startswith(" "):
                        spaceFilter = spaceFilter.replace(" ", "", 1)
                    temp["AudioFilename"] = spaceFilter
                elif "PreviewTime:" in line and (rq_type == "audio" or rq_type == "preview" or rq_type == "all"):
                    spaceFilter = line.replace("PreviewTime:", "").replace("\n", "")
                    if spaceFilter.startswith(" "):
                        spaceFilter = spaceFilter.replace(" ", "", 1)
                    temp["PreviewTime"] = spaceFilter
                #비트맵별 BG 파일이름
                elif ('"' and ".jpg") in lineCheck and not bg_ignore and (rq_type == "bg" or rq_type == "thumb" or rq_type == "all"):
                    temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                    bg_ignore = True
                elif ('"' and ".png") in lineCheck and not bg_ignore and (rq_type == "bg" or rq_type == "thumb" or rq_type == "all"):
                    temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                    bg_ignore = True
                elif ('"' and ".jpeg") in lineCheck and not bg_ignore and (rq_type == "bg" or rq_type == "thumb" or rq_type == "all"):
                    temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                    bg_ignore = True
                #비트맵별 video 파일이름
                #.avi 추가하기
                #elif '"' and "Video" and ".mp4" in line:
                elif '"' and "video" and ".mp4" in lineCheck and (rq_type == "video" or rq_type == "all"):
                    temp["BeatmapVideo"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                elif '"' and ".mp4" in lineCheck and (rq_type == "video" or rq_type == "all") and underV10:
                    temp["BeatmapVideo"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                temp["beatmapName"] = beatmapName
        try:
            temp["BeatmapVideo"] is None
        except:
            temp["BeatmapVideo"] = None """
        beatmap_info.append(temp)

    bidsList = [i["BeatmapID"] for i in beatmap_info]
    md5sList = [i["BeatmapMD5"] for i in beatmap_info]
    verList = [i["Version"] for i in beatmap_info]

    #bid 0 변경
    for zero in [y for y, x in enumerate(bidsList) if x == 0]:
        log.warning(f"bid 0 발견! | {md5sList[zero]}")
        try:
            bidsList[zero] = dbR.fetch("SELECT beatmap_id FROM beatmaps WHERE beatmap_md5 = %s", [md5sList[zero]])["beatmap_id"]
        except:
            try:
                bidsList[zero] = dbR.fetch("SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s", [setID, verList[zero]])["id"]
            except:
                log.warning("0 | RealBid가 redstarDB + cheesegull에서 조회되지 않음! 스킵함")
                bidsList[zero] = 0
        for bi, b, m in zip(beatmap_info, bidsList, md5sList):
            if bi["BeatmapMD5"] == m:
                bi["BeatmapID"] = b

    #중복 bid 찾기
    dup = [item for item, cnt in Counter(bidsList).items() if cnt > 1]
    if len(dup) != 0:
        log.warning("bid 중복 있음!")
        for i in dup:
            #중복 bid list index위치 찾기
            for idx in [y for y, x in enumerate(bidsList) if x == i]:
                #중복 bid 수정
                try:
                    bidsList[idx] = dbR.fetch("SELECT beatmap_id FROM beatmaps WHERE beatmap_md5 = %s", [md5sList[idx]])["beatmap_id"]
                except:
                    try:
                        bidsList[idx] = dbC.fetch("SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s", [setID, verList[idx]])["id"]
                    except:
                        log.warning("0 | RealBid가 cheesegull에서 조회되지 않음! 스킵함")
                        bidsList[idx] = 0
                for bi, b, m in zip(beatmap_info, bidsList, md5sList):
                    if bi["BeatmapMD5"] == m:
                        bi["BeatmapID"] = b
        
        #[log.debug(i) for i in beatmap_info]

    if int(setID) > 0:
        first_bid = min([x for x in bidsList if x > 0])
    else:
        first_bid = min([x for x in bidsList])

    if not moving:
        shutil.rmtree(f"{dataFolder}/dl/{setID}")
    return [int(setID), first_bid, beatmap_info]

def move_files(setID, rq_type):
        isOsuFile = False
        result = osu_file_read(setID, rq_type, moving=True)
        #필요한 파일만 각 폴더로 이동
        for item in result[2]:
            isOsuFile = True
            #아래 코드 에러 방지용 (폴더가 없으면 에러남)
            if not os.path.isdir(f"{dataFolder}/bg/{setID}") and rq_type == "bg":
                os.mkdir(f"{dataFolder}/bg/{setID}")
                log.info(f"{dataFolder}/bg/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"{dataFolder}/thumb/{setID}") and rq_type == "thumb":
                os.mkdir(f"{dataFolder}/thumb/{setID}")
                log.info(f"{dataFolder}/thumb/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"{dataFolder}/audio/{setID}") and rq_type == "audio":
                os.mkdir(f"{dataFolder}/audio/{setID}")
                log.info(f"{dataFolder}/audio/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"{dataFolder}/preview/{setID}") and rq_type == "preview":
                os.mkdir(f"{dataFolder}/preview/{setID}")
                log.info(f"{dataFolder}/preview/{setID} 폴더 생성 완료!")
            try:
                if not os.path.isdir(f"{dataFolder}/video/{setID}") and item["BeatmapVideo"] is not None and rq_type == "video":
                    os.mkdir(f"{dataFolder}/video/{setID}")
                    log.info(f"{dataFolder}/video/{setID} 폴더 생성 완료!")
            except:
                #log.warning(f"{item['BeatmapID']} bid no video")
                pass
            if not os.path.isdir(f"{dataFolder}/osu/{setID}") and not IS_YOU_HAVE_OSU_PRIVATE_SERVER and rq_type == "osu":
                os.mkdir(f"{dataFolder}/osu/{setID}")
                log.info(f"{dataFolder}/osu/{setID} 폴더 생성 완료!")

            #log.debug(item)

            #BeatmapSetID용 미리듣기 + BG (b.redstar.moe/preview?예정)
            if item["BeatmapID"] == result[1]:
                if rq_type == "bg":
                    try:
                        extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                        shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapBG']}", f"{dataFolder}/bg/{setID}/+{setID}{extension}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | BG 처리함")
                    except:
                        log.error(f"{setID} 비트맵셋은 BG가 없음 | no image.png로 저장함")
                        shutil.copy(f"static/img/no image.png", f"{dataFolder}/bg/{setID}/+{setID}.png")

                if rq_type == "thumb":
                    try:
                        extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                        shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapBG']}", f"{dataFolder}/thumb/{setID}/+{setID}{extension}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | thumb 처리함")
                    except:
                        log.error(f"{setID} 비트맵셋은 thumb가 없음 | no image.png로 저장함")
                        shutil.copy(f"static/img/no image.png", f"{dataFolder}/thumb/{setID}/+{setID}.png")

                if rq_type == "preview":
                    try:
                        shutil.copy(f"{dataFolder}/dl/{setID}/{item['AudioFilename']}", f"{dataFolder}/preview/{setID}/{item['AudioFilename']}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | {item['AudioFilename']} 처리함")
                    except:
                        shutil.copy(f"static/audio/no audio.mp3", f"{dataFolder}/preview/{setID}/no audio_{setID}.mp3")
                        log.error(f"{setID} 비트맵셋은 preview가 없음 | no audio_{setID}.mp3로 저장하고, preview도 처리함")

            if rq_type == "bg":
                try:
                    extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapBG']}", f"{dataFolder}/bg/{setID}/{item['BeatmapID']}{extension}")
                    log.info(f"{item['BeatmapID']} 비트맵 | BG 처리함")
                except:
                    log.error(f"{item['BeatmapID']} 비트맵은 BG가 없음 | no image.png로 저장함")
                    shutil.copy(f"static/img/no image.png", f"{dataFolder}/bg/{setID}/{item['BeatmapID']}.png")

            if rq_type == "audio":
                try:
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['AudioFilename']}", f"{dataFolder}/audio/{setID}/{item['AudioFilename']}")
                    log.info(f"{item['BeatmapID']} 비트맵 | audio 처리함")
                except:
                    log.error(f"{item['BeatmapID']} 비트맵은 audio가 없음 | no audio.mp3로 저장함")
                    shutil.copy(f"static/audio/no audio.mp3", f"{dataFolder}/audio/{setID}/no audio.mp3")

            if rq_type == "video":
                try:
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['BeatmapVideo']}", f"{dataFolder}/video/{setID}/{item['BeatmapVideo']}")
                    log.info(f"{item['BeatmapID']} 비트맵은 video가 존재함!")
                except:
                    pass
            
            if not IS_YOU_HAVE_OSU_PRIVATE_SERVER and rq_type == "osu":
                shutil.copy(f"{dataFolder}/dl/{setID}/{item['beatmapName']}", f"{dataFolder}/osu/{setID}/{item['BeatmapID']}.osu")
                log.info(f"{item['BeatmapID']} 비트맵 | osu 처리함")

            #lets | read_osu
            if rq_type.startswith("read_osu"):
                bid = int(rq_type.replace("read_osu_", ""))
                if int(item['BeatmapID']) == bid:
                    log.info(rq_type)
                    shutil.copy(f"{dataFolder}/dl/{setID}/{item['beatmapName']}", f"{lets_beatmaps_Folder}/{bid}.osu")
                    log.info(f"{bid}.osu | lets에 넣음")
                    shutil.rmtree(f"{dataFolder}/dl/{setID}")
                    return 0

        if not isOsuFile:
            raise FileNotFoundError(f".osu 파일이 존재하지 않는것으로 보임! | [WinError 3] 지정된 경로를 찾을 수 없습니다: '{dataFolder}/{rq_type}/{setID}'")

        #osu_file_read() 함수에 인자값으로 True를 넣어서 dl/{setID} 가 삭제 되지 않으므로 여기서 폴더 삭제함
        shutil.rmtree(f"{dataFolder}/dl/{setID}")

def check(setID, rq_type, checkRenewFile=False, site=0):
    #.osz는 무조건 새로 받되, Bancho, Redstar**전용** 맵에서 ranked, loved 등등 은 새로 안받아도 댐. (Redstar에서의 랭크상태 여부는 고민중)
    #근데 생각해보니 파일 있으면 걍 이걸 안오는데?
    folder_check()
    fullSongName = get_osz_fullName(setID)
    log.debug(fullSongName)

    if fullSongName == f"{setID} .osz":
        log.error(f"{fullSongName} | 존재는 하나 꺠지거나 문제가 있음. 재 다운로드중...")
        fullSongName = 0

    url = [f'https://api.nerinyan.moe/d/{setID}', f"https://chimu.moe/d/{setID}"]

    limit = 0
    def dl(site, limit):
        #우선 setID .osz로 다운받고 나중에 파일 이름 변경
        file_name = f'{setID} .osz' #919187 765 MILLION ALLSTARS - UNION!!.osz, 2052147 (Love Live! series) - Colorful Dreams! Colorful Smiles! _  TV2
        save_path = f'{dataFolder}/dl/'  # 원하는 저장 경로로 변경
        
        # 파일 다운로드 요청
        try:
            res = requests.get(url[site], headers=requestHeaders, timeout=5, stream=True)
            statusCode = res.status_code
        except requests.exceptions.ReadTimeout as e:
            log.warning(f"{url[site]} Timeout! | e = {e}")
            statusCode = 504
        except:
            log.error(f"파일다운 기본 예외처리 | url = {url[site]}")

        if statusCode == 200:
            # 파일 크기를 얻습니다.
            file_size = int(res.headers.get('content-length', 0))

            # tqdm을 사용하여 진행률 표시
            with open(save_path + file_name, 'wb') as file:
                with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, ncols=120) as pbar:
                    for data in res.iter_content(1024):
                        file.write(data)
                        pbar.update(len(data))

            header_filename = res.headers['content-disposition']
            newFilename = header_filename[header_filename.find('filename='):].replace("filename=", "").replace('"', "")
            if site == 1 and  "%20" in newFilename:
                newFilename = newFilename.replace("%20", " ")
            newFilename = re.sub(r'[<>:"/\\|?*]', '_', newFilename)

            log.info(f'{file_name} --> {newFilename} 다운로드 완료')

            # WAV 파일 재생을 별도의 스레드에서 수행
            def play_finished_dl():
                #winsound.PlaySound("static/audio/match-confirm (mp3cut.net).wav", winsound.SND_FILENAME)
                PlaySound(AudioSegment.from_file("static/audio/match-confirm (mp3cut.net).wav"))
            play_thread = threading.Thread(target=play_finished_dl)
            play_thread.start()

            try:
                os.rename(f"{dataFolder}/dl/{setID} .osz", f"{dataFolder}/dl/{newFilename}")
            except FileExistsError:
                os.replace(f"{dataFolder}/dl/{newFilename}", f"{dataFolder}/dl/{newFilename}-old")
                os.replace(f"{dataFolder}/dl/{setID} .osz", f"{dataFolder}/dl/{newFilename}")
            return statusCode
        else:
            log.error(f'{statusCode}. 파일을 다운로드할 수 없습니다. chimu로 재시도!')
            limit += 1
            if limit < 3:
                return dl(1, limit)
            else:
                log.warning(f"다운로드 요청 자체 limit 걸음! {limit}번 요청함")
                return statusCode

    if fullSongName == 0:
        log.warning(f"{setID} 맵셋 osz 존재하지 않음. 다운로드중...")
        dlsc = dl(site, limit=0)
    elif fullSongName != 0 and site == 1:
        log.warning(f"{setID} 파일 깨진거로 간주하고 chimu에서 새로 다운로드중...")
        dlsc = dl(site, limit=0)
    else:
        dlsc = 200
        log.info(f"{get_osz_fullName(setID)} 존재함")

        """ exceptOszList = [919187, 871623, 12483, 1197242, 1086293, 940322, -10000000]
        exceptOszList.append(929972) #네리냥에서 깨진 맵임 버그리봇방에 올려둠
        exceptOszList.append(1745195)
        exceptOszList.append(645756) """ #Update by <t:1706294656>

        with open("exceptOszList.json", "r") as file:
            exceptOszList = json.load(file)
            exceptOszList = exceptOszList["exceptOszList"] + exceptOszList["exceptOszList2"]

        #7일 이상 된 비트맵만 파일체크함
        fED = os.path.getmtime(f"data/dl/{get_osz_fullName(setID)}")
        t = round(time.time() - fED)
        if t > oszRenewTime:
            fED = True
        else:
            fED = False
        log.info(f"t:{t} > oszRenewTime:{oszRenewTime} = {t > oszRenewTime} | 최종 조건 = {checkRenewFile and int(setID) not in exceptOszList and fED}")

        #이거 redstar DB에 없는 경우 있으니 cheesegull DB에서도 추가로 참고하기
        if checkRenewFile and int(setID) not in exceptOszList and fED:
            try:
                rankStatus = dbR.fetch(f"SELECT ranked FROM beatmaps WHERE beatmapset_id = %s", [setID])["ranked"]
                log.info(f"파일 최신화 redstar DB 랭크상태 조회 완료 : {rankStatus}")
                if rankStatus == 4:
                    rankStatus = 0
            except:
                rankStatus = dbC.fetch(f"SELECT ranked_status FROM sets WHERE id = %s", [setID])["ranked_status"]
                log.info(f"파일 최신화 cheesegull DB 랭크상태 조회 완료 : {rankStatus}")
            if rankStatus <= 0:
                oszHash = calculate_md5(f"{dataFolder}/dl/{fullSongName}")
                log.debug(f"oszHash = {oszHash}")
                for i in url:
                    newOszHash = requests.get(i, headers=requestHeaders, timeout=5, stream=True)
                    if newOszHash.status_code == 200:
                        # tqdm을 사용하여 진행률 표시
                        with open(f"{dataFolder}/dl/t{setID} .osz", 'wb') as file:
                            with tqdm(total=int(newOszHash.headers.get('content-length', 0)), unit='B', unit_scale=True, unit_divisor=1024, ncols=60) as pbar:
                                for data in newOszHash.iter_content(1024):
                                    file.write(data)
                                    pbar.update(len(data))
                        newOszHash = calculate_md5(f"{dataFolder}/dl/t{setID} .osz")
                        log.debug(f"oszHash = {oszHash} | newOszHash = {newOszHash}")
                        if oszHash != newOszHash:
                            log.warning(f"{setID} 가 최신이 아닙니다!")
                            try:
                                shutil.copy2(f"{dataFolder}/dl/{fullSongName}", f"{dataFolder}/dl-old/{fullSongName[:-4]}-{time.time()}.osz")
                            except IOError as e:
                                log.error(f"파일 복사 중 오류 발생: {e}")
                            log.info(f"{removeAllFiles(setID)}\n")
                            os.replace(f"{dataFolder}/dl/t{setID} .osz", f"{dataFolder}/dl/{fullSongName}")
                        else:
                            os.remove(f"{dataFolder}/dl/t{setID} .osz")
                            os.utime(f"{dataFolder}/dl/{fullSongName}", (time.time(), time.time()))
                        break
                    else:
                        continue

    if checkRenewFile:
        return None
    elif dlsc != 200:
        return dlsc
    else:
        try:
            move_files(setID, rq_type)
        except Exception as e:
            return e
            
def crf(bsid, rq_type):
    #파일 최신화
    if rq_type == "osz":
        ck = check(bsid, rq_type, checkRenewFile=True)
        if ck is not None:
            return ck
    else:
        pass

#######################################################################################################################################

def read_list(bsid=""):
    result = {}

    if bsid == "":
        osz_file_list = [file for file in os.listdir(f"{dataFolder}/dl/")]
        result["osz"] = {"list": osz_file_list, "count": len(osz_file_list)}
    else:
        osz_file_list = [get_osz_fullName(bsid)]
        result["osz"] = {"list": osz_file_list, "count": len(osz_file_list)}

    bg_file_list = [file for file in os.listdir(f"{dataFolder}/bg/{bsid}")]
    result["bg"] = {"list": bg_file_list, "count": len(bg_file_list)}

    thumb_file_list = [file for file in os.listdir(f"{dataFolder}/thumb/{bsid}")]
    result["thumb"] = {"list": thumb_file_list, "count": len(thumb_file_list)}

    audio_file_list = [file for file in os.listdir(f"{dataFolder}/audio/{bsid}")]
    result["audio"] = {"list": audio_file_list, "count": len(audio_file_list)}

    preview_file_list = [file for file in os.listdir(f"{dataFolder}/preview/{bsid}")]
    result["preview"] = {"list": preview_file_list, "count": len(preview_file_list)}

    try:
        video_file_list = [file for file in os.listdir(f"{dataFolder}/video/{bsid}")]
        result["video"] = {"list": video_file_list, "count": len(video_file_list)}
    except:
        result["video"] = {"list": "NO FOLDER", "count": 0}

    try:
        osu_file_list = [file for file in os.listdir(f"{dataFolder}/osu/{bsid}")]
        result["osu"] = {"list": osu_file_list, "count": len(osu_file_list)}
    except:
        result["osu"] = {"list": "NO FOLDER", "count": 0}

    return result

def read_bg(id):
    if "+" in id:
        id = str(id).replace("+", "")

        #파일 최신화
        crf(id, rq_type="bg")

        #bg폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/bg/{id}"):
            #파일 다운로드시에 500 뜨면 500 코드로 반환 예정, 만약 우리서버 문제면 main.py 에서 503 코드로 반환
            ck = check(id, rq_type="bg")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/bg/{id}") if file.startswith("+")]
        try:
            print(file_list[0])
        except:
            log.error(f"bsid = {id} | BG print(file_list[0]) 에러")
            ck = check(id, rq_type="bg")
            if ck is not None:
                return ck
            return read_bg(f"+{id}")
        return f"{dataFolder}/bg/{id}/{file_list[0]}"
    else:
        try:
            bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
        except:
            try:
                bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
                log.info("RedstarOSU DB에서 bsid 찾음")
            except:
                raise KeyError("Not Found bsid!")

        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #파일 최신화
        crf(bsid, rq_type="bg")

        #bg폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/bg/{bsid}"):
            ck = check(bsid, rq_type="bg")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/bg/{bsid}") if file.startswith(str(id))]
        try:
            print(file_list[0])
        except:
            log.error(f"bid = {id} | BG print(file_list[0]) 에러")
            ck = check(bsid, rq_type="bg")
            if ck is not None:
                return ck
            return read_bg(id)
        return f"{dataFolder}/bg/{bsid}/{file_list[0]}"
    
def read_thumb(id):
    if "l.jpg" in id:
        bsid = id.replace("l.jpg", "")
        img_size = (160, 120)
    else:
        bsid = id.replace(".jpg", "")
        img_size = (80, 60)

    #파일 최신화
    crf(bsid, rq_type="thumb")

    if os.path.isfile(f"{dataFolder}/thumb/{bsid}/{id}"):
        return f"{dataFolder}/thumb/{bsid}/{id}"
    else:
        #thumb폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/thumb/{bsid}"):
            ck = check(bsid, rq_type="thumb")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/thumb/{bsid}") if file.startswith("+")]
        try:
            print(file_list[0])
        except:
            log.error(f"bsid = {bsid} | thumb print(file_list[0]) 에러")
            ck = check(bsid, rq_type="thumb")
            if ck is not None:
                return ck
            return read_thumb(id)

        img = Image.open(f"{dataFolder}/thumb/{bsid}/{file_list[0]}")
        # 이미지 모드를 RGBA에서 RGB로 변환
        img = img.convert("RGB")

        width, height = img.size
        left = (width - (height * (4 / 3))) / 2
        top = 0
        right = width - left
        bottom = height
        
        img_cropped = img.crop((left,top,right,bottom))
        img_resize = img_cropped.resize(img_size, Image.LANCZOS)
        img_resize.save(f"{dataFolder}/thumb/{bsid}/{id}", quality=100)

        os.remove(f"{dataFolder}/thumb/{bsid}/{file_list[0]}")

        return f"{dataFolder}/thumb/{bsid}/{id}"

#osu_file_read() 역할 분할하기 (각각 따로 두기)
def read_audio(id):
    #ffmpeg -i "audio.ogg" -acodec libmp3lame -q:a 0 -y "audio.mp3"
    def audioSpeed(mods, setID, file_list):
        #변환 시작 + 에러시 코덱 확인후 재 변환
        Codec = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", f"{dataFolder}/audio/{setID}/{file_list[0]}"], stderr=subprocess.STDOUT).decode().replace("\r", "").replace("\n", "")
        if Codec != "mp3":
            log.error(f"{file_list[0]} 코텍은 mp3가 아님 | {Codec}")

        if mods == "DT":
            DTFilename = f"{dataFolder}/audio/{setID}/{file_list[0][:-4]}-DT.mp3"
            if os.path.isfile(DTFilename):
                return DTFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/audio/{setID}/{file_list[0]}" -af atempo=1.5 -acodec libmp3lame -q:a 0 -y "{DTFilename}"'
                log.chat(f"DT ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return DTFilename
        elif mods == "NC":
            NCFilename = f"{dataFolder}/audio/{setID}/{file_list[0][:-4]}-NC.mp3"
            if os.path.isfile(NCFilename):
                return NCFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/audio/{setID}/{file_list[0]}" -af asetrate={AudioSegment.from_file(f"{dataFolder}/audio/{setID}/{file_list[0]}").frame_rate}*1.5 -acodec libmp3lame -q:a 0 -y "{NCFilename}"'
                log.chat(f"NC ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return NCFilename
        elif mods == "HF":
            HFFilename = f"{dataFolder}/audio/{setID}/{file_list[0][:-4]}-HF.mp3"
            if os.path.isfile(HFFilename):
                return HFFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/audio/{setID}/{file_list[0]}" -af atempo=0.75 -acodec libmp3lame -q:a 0 -y "{HFFilename}"'
                log.chat(f"HF ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return HFFilename
        else:
            return f"{dataFolder}/audio/{setID}/{file_list[0]}"

    if "+" in id:
        id = str(id).replace("+", "")
        if id.upper()[-2:] == "DT":
            log.chat("DT 감지")
            mods = "DT"
            id = id[:-2]
        elif id.upper()[-2:] == "NC":
            log.chat("NC 감지")
            mods = "NC"
            id = id[:-2]
        elif id.upper()[-2:] == "HF":
            log.chat("HF 감지")
            mods = "HF"
            id = id[:-2]
        else:
            mods = None

        #파일 최신화
        crf(id, rq_type="audio")

        #audio폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/audio/{id}"):
            ck = check(id, rq_type="audio")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/audio/{id}")]

        if len(file_list) > 1:
            AF = osu_file_read(id, rq_type="audio")
            for i in AF[2]:
                if AF[1] == i["BeatmapID"]:
                    file_list = [i['AudioFilename']]

        try:
            print(file_list[0])
        except:
            log.error(f"bsid = {id} | audio print(file_list[0]) 에러")
            ck = check(id, rq_type="audio")
            if ck is not None:
                return ck
            
            if mods == "DT":
                return read_audio(f"+{id}DT")
            elif mods == "NC":
                return read_audio(f"+{id}NC")
            elif mods == "HF":
                return read_audio(f"+{id}HF")
            else:
                return read_audio(f"+{id}")

        return audioSpeed(mods, id, file_list)
    else:
        if id.upper()[-2:] == "DT":
            log.chat("DT 감지")
            mods = "DT"
            id = id[:-2]
        elif id.upper()[-2:] == "NC":
            log.chat("NC 감지")
            mods = "NC"
            id = id[:-2]
        elif id.upper()[-2:] == "HF":
            log.chat("HF 감지")
            mods = "HF"
            id = id[:-2]
        else:
            mods = None

        #파일 최신화
        crf(id, rq_type="audio")

        try:
            bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
        except:
            try:
                bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
                log.info("RedstarOSU DB에서 bsid 찾음")
            except:
                raise KeyError("Not Found bsid!")

        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #audio폴더 파일 체크
        if not os.path.isdir(f"{dataFolder}/audio/{bsid}"):
            ck = check(bsid, rq_type="audio")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"{dataFolder}/audio/{bsid}")]

        if len(file_list) > 1:
            AF = osu_file_read(bsid, rq_type="audio")
            for i in AF[2]:
                if int(id) == i["BeatmapID"]:
                    file_list = [i['AudioFilename']]

        try:
            print(file_list[0])
        except:
            log.error(f"bid = {id} | audio print(file_list[0]) 에러")
            ck = check(bsid, rq_type="audio")
            if ck is not None:
                return ck
            
            if mods == "DT":
                return read_audio(f"{id}DT")
            elif mods == "NC":
                return read_audio(f"{id}NC")
            elif mods == "HF":
                return read_audio(f"{id}HF")
            else:
                return read_audio(id)

        return audioSpeed(mods, bsid, file_list)

def read_preview(id):
    #source_{bsid}.mp3 먼저 확인시키기 ㄴㄴ audio에서 가져오기
    setID = id.replace(".mp3", "")

    #파일 최신화
    crf(setID, rq_type="preview")

    if not os.path.isfile(f"{dataFolder}/preview/{setID}/{id}"):
        if os.path.isfile(f"{dataFolder}/preview/{setID}/no audio_{id}"):
            #위에서 오디오 없어서 이미 처리댐 (no audio.mp3)
            log.warning(f"no audio_{id}")
            return f"{dataFolder}/preview/{setID}/no audio_{id}"
        else:
            ck = check(setID, rq_type="preview")
            if ck is not None:
                return ck
        
        if os.path.isfile(f"{dataFolder}/preview/{setID}/no audio_{id}"):
            #위에서 오디오 없어서 이미 처리댐 (no audio.mp3)
            log.warning(f"no audio_{id}")
            return f"{dataFolder}/preview/{setID}/no audio_{id}"

        #음원 하이라이트 가져오기, 밀리초라서 / 1000 함
        PreviewTime = -1
        AudioFilename = ""
        j = osu_file_read(setID, rq_type="preview")
        
        for i in j[2]:
            if j[1] == i["BeatmapID"]:
                prti = int(i["PreviewTime"])
                AudioFilename = i["AudioFilename"]
                if prti == -1:
                    audio = AudioSegment.from_file(f"{dataFolder}/preview/{setID}/{AudioFilename}")
                    PreviewTime = len(audio) / 1000 / 2.5
                    log.warning(f"{setID}.mp3 ({AudioFilename}) 의 PreviewTime 값이 {prti} 이므로 TotalLength / 2.5 == {PreviewTime} 로 세팅함")
                else:
                    PreviewTime = prti / 1000
        
        if AudioFilename.endswith(".mp3"):
            ffmpeg_msg = f'ffmpeg -i "{dataFolder}/preview/{setID}/{AudioFilename}" -ss {PreviewTime} -t 30.821 -acodec copy -y "{dataFolder}/preview/{setID}/{id}"'
        else:
            ffmpeg_msg = f'ffmpeg -i "{dataFolder}/preview/{setID}/{AudioFilename}" -ss {PreviewTime} -t 30.821 -acodec libmp3lame -q:a 0 -y "{dataFolder}/preview/{setID}/{id}"'
            log.warning(f"ffmpeg_msg = {ffmpeg_msg}")
        
        log.chat(f"ffmpeg_msg = {ffmpeg_msg}")
        #변환 시작 + 에러시 코덱 확인후 재 변환
        if os.system(ffmpeg_msg) != 0:
            Codec = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", f"{dataFolder}/preview/{setID}/{AudioFilename}"], stderr=subprocess.STDOUT).decode().replace("\r", "").replace("\n", "")
            log.error(f"ffmpeg .mp3 변환 실패! | 코덱 조회: {Codec}")
            if Codec != "mp3":
                ffmpeg_msg = f'ffmpeg -i "{dataFolder}/preview/{setID}/{AudioFilename}" -ss {PreviewTime} -t 30.821 -acodec libmp3lame -q:a 0 -y "{dataFolder}/preview/{setID}/{id}"'
                if os.system(ffmpeg_msg) != 0:
                    log.error(f"{setID} | {AudioFilename} 변환 실패!")

        os.remove(f"{dataFolder}/preview/{setID}/{AudioFilename}")
    return f"{dataFolder}/preview/{setID}/{id}"

def read_video(id):
    try:
        bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    #파일 최신화
    crf(bsid, rq_type="video")

    #video폴더 파일 체크
    if not os.path.isdir(f"{dataFolder}/video/{bsid}"):
        ck = check(bsid, rq_type="video")
        if ck is not None:
            return ck

    hasVideo = next((i["BeatmapVideo"] for i in osu_file_read(bsid, rq_type="video")[2] if int(id) == i["BeatmapID"]), None)
    if hasVideo is None:
        log.warning(f"{id} 해당 비트맵은 .osu 파일에 비디오 정보가 없습니다!")
        try:
            #hasVideo = dbC.fetch("SELECT has_video FROM sets WHERE id = %s", [bsid])["has_video"]
            #반초로 조회함
            hasVideo = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_APIKEY}&b={id}", headers=requestHeaders)
            hasVideo = int(hasVideo.json()[0]["video"])

            if hasVideo != 0:
                file_list = [file for file in os.listdir(f"{dataFolder}/video/{bsid}") if file.endswith(".mp4")]
                if len(file_list) > 1:
                    AF = osu_file_read(bsid, rq_type="video")
                    for i in AF[2]:
                        if int(id) == i["BeatmapID"]:
                            file_list = [i['AudioFilename']]
                try:
                    #log.debug(print(file_list[0]))
                    print(file_list[0])
                except:
                    log.error(f"bid = {id} | video print(file_list[0]) 에러")
                    ck = check(bsid, rq_type="video")
                    if ck is not None:
                        return ck
                    return read_video(id)
                return f"{dataFolder}/video/{bsid}/{file_list[0]}"
            else:
                raise
        except:
            return f"{id} Beatmap has no video!"
    else:
        #임시로 try 박아둠, 나중에 반초라던지 비디오 있나 요청하는거로 바꾸기
        if os.path.isfile(f"{dataFolder}/video/{bsid}/{hasVideo}"):
            return f"{dataFolder}/video/{bsid}/{hasVideo}"
            

def read_osz(id):
    #파일 최신화
    crf(id, rq_type="osz")

    filename = get_osz_fullName(id)
    if filename != f"{id} .osz" and os.path.isfile(f"{dataFolder}/dl/{filename}"):
        return {"path": f"{dataFolder}/dl/{filename}", "filename": filename}
    else:
        ck = check(id, rq_type="osz")
        if ck is not None:
            return ck
        newFilename = get_osz_fullName(id)
        if os.path.isfile(f"{dataFolder}/dl/{newFilename}"):
            return {"path": f"{dataFolder}/dl/{newFilename}", "filename": newFilename}
        else:
            return 0

def read_osz_b(id):
    try:
        bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
    return read_osz(bsid)

def read_osu(id):
    try:
        bsid = dbC.fetch("SELECT parent_set_id FROM beatmaps WHERE id = %s", [id])["parent_set_id"]
    except:
        try:
            bsid = dbR.fetch("SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = %s", [id])["beatmapset_id"]
            log.info("RedstarOSU DB에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

    #파일 최신화
    crf(bsid, rq_type=f"read_osu_{id}")

    #B:\redstar\lets\.data\beatmaps 우선시함
    if os.path.isfile(f"{lets_beatmaps_Folder}/{id}.osu"):
        log.info(f"{id}.osu 파일을 {lets_beatmaps_Folder}/{id}.osu에서 먼저 찾아서 반환함")
        
        sql = '''
            SELECT CONCAT(s.artist, ' - ', s.title, ' (', s.creator, ') [', b.diff_name, ']' '.osu') AS filename
            FROM sets AS s
            JOIN beatmaps AS b ON s.id = b.parent_set_id
            WHERE b.id = %s
        '''
        filename = dbC.fetch(sql, [id])
        log.debug(filename)
        if filename is None:
            log.error(f"filename is None | sql = {sql}")
            return None
        return {"path": f"{lets_beatmaps_Folder}/{id}.osu", "filename": filename["filename"]}
    else:
        ck = check(bsid, rq_type=f"read_osu_{id}")
        if ck is not None:
            return ck
        return read_osu(id)
    
    if os.path.isfile(f"{dataFolder}/osu/{bsid}/{id}.osu"):
        return {"path": f"{dataFolder}/osu/{bsid}/{id}.osu", "filename": filename}
    else:
        ck = check(bsid, rq_type=f"read_osu_{id}")
        if ck is not None:
            return ck
        return read_osu(id)

def filename_to_GetCheesegullDB(filename):
    try:
        parentheses = filename.count(" (")
        if parentheses == 1:
            # 정규식 패턴
            pattern = r"^(.+) - (.+) \(([^)]+)\) \[([^]]+)\]\.osu$"
            match = re.match(pattern, filename)

            artist = match.group(1)
            title = match.group(2)
            creator = match.group(3)
            version = match.group(4)
        elif parentheses == 0:
            # 정규식 패턴
            pattern = r"^(.+) - (.+) \[([^]]+)\]\.osu$"
            match = re.match(pattern, filename)

            artist = match.group(1)
            title = match.group(2)
            creator = match.group(3)
            version = match.group(4)
        else:
            # 정규식 패턴
            pattern = r"^(.+) - (.+) (\([^()]+\)) \(([^()]+)\) \[([^]]+)\]\.osu$"
            match = re.match(pattern, filename)

            artist = match.group(1)
            title = f"{match.group(2)} {match.group(3)}"
            creator = match.group(4)
            version = match.group(5)
    except:
        artist = None
        title = None
        creator = None
        version = None
        log.error("osu filename에서 artist, title, creator, version 추출중 에러")

    """ try:
        artist = filename[:filename.find(" - ")]
        title = filename[(filename.find(" - ") + 3):filename.find(" (")]
        creator = filename[(filename.find(" (") + 1 + 1):(filename.find(") ["))]
        version = filename[(filename.find(") [") + 1 + 2):filename.find("].osu")]
    except:
        log.error("osu filename에서 artist, title, creator, version 추출중 에러") """

    # filename에 / 가 들어가면 에러남 (http 요청시 / 가 사라짐)
    sql = '''
        SELECT b.id, b.parent_set_id, b.diff_name
        FROM beatmaps AS b
        JOIN sets AS s ON b.parent_set_id = s.id
        WHERE s.artist = %s AND s.title = %s AND s.creator = %s AND b.diff_name = %s
    '''
    result = dbC.fetch(sql, [artist, title, creator, version])
    if result is None:
        #특수문자 등등 조회 안되는거 짤라서 조회
        log.warning("filename 조회 실패! | 단어별로 짤라서 찾아봄")

        artist_sp = artist.split()
        title_sp = title.split()
        creator_sp = creator.split()
        version_sp = version.split()

        sql_part = '''
            SELECT b.id, b.parent_set_id, b.diff_name
            FROM beatmaps AS b
            JOIN sets AS s ON b.parent_set_id = s.id
            WHERE
        '''
        param_part = []
        for i, v in enumerate(artist_sp):
            if i == 0:
                sql_part += " s.artist LIKE %s"
                param_part.append(f"{v}%")
            else:
                sql_part += " AND s.artist LIKE %s"
                param_part.append(f"%{v}%")
        for i, v in enumerate(title_sp):
            if i == 0:
                sql_part += " AND s.title LIKE %s"
                param_part.append(f"{v}%")
            else:
                sql_part += " AND s.title LIKE %s"
                param_part.append(f"%{v}%")
        for i, v in enumerate(creator_sp):
            if i == 0:
                sql_part += " AND s.creator LIKE %s"
                param_part.append(f"{v}%")
            else:
                sql_part += " AND s.creator LIKE %s"
                param_part.append(f"%{v}%")
        for i, v in enumerate(version_sp):
            if i == 0:
                sql_part += " AND b.diff_name LIKE %s"
                param_part.append(f"{v}%")
            else:
                sql_part += " AND b.diff_name LIKE %s"
                param_part.append(f"%{v}%")

        result_part = dbC.fetch(sql_part, param_part)
        if result_part is None:
            return None
        elif type(result_part) == list and len(result_part) > 1:
            log.warning(f"값이 2개 이상임 ({len(result_part)}) | result_part = {result_part}")
            return None
        else:
            return result_part
    else:
        return result

def read_osu_filename(filename):
    result = filename_to_GetCheesegullDB(filename)
    log.debug(f"result = {result}")
    if result is None:
        #Bancho에 이름으로 bid 찾는 방법 찾아내기
        return None
    bid = result["id"]
    return read_osu(bid)

def removeAllFiles(bsid):
    osz = get_osz_fullName(bsid)

    isdelosz = 0
    isdelbg = 0
    isdelthumb = 0
    isdelaudio = 0
    isdelpreview = 0
    isdelvideo = 0
    isdelosu = 0
    print("")

    #osz
    if osz == 0:
        log.error(f"{bsid} osz는 존재하지 않음")
    else:
        try:
            os.remove(f"{dataFolder}/dl/{osz}")
            log.info(f'파일 {osz} 가 삭제되었습니다.')
            isdelosz = 1
        except OSError as e:
            log.error(f'파일 삭제 실패: {e}')
    try:
        shutil.rmtree(f"{dataFolder}/dl/{bsid}")
        log.info(f'폴더 {dataFolder}/dl/{bsid} 가 삭제되었습니다.')
    except:
        pass

    #bg
    try:
        shutil.rmtree(f"{dataFolder}/bg/{bsid}")
        log.info(f'폴더 {dataFolder}/bg/{bsid} 가 삭제되었습니다.')
        isdelbg = 1
    except:
        pass

    #thumb
    try:
        shutil.rmtree(f"{dataFolder}/thumb/{bsid}")
        log.info(f'폴더 {dataFolder}/thumb/{bsid} 가 삭제되었습니다.')
        isdelthumb = 1
    except:
        pass

    #audio
    try:
        shutil.rmtree(f"{dataFolder}/audio/{bsid}")
        log.info(f'폴더 {dataFolder}/audio/{bsid} 가 삭제되었습니다.')
        isdelaudio = 1
    except:
        pass

    #preview
    try:
        shutil.rmtree(f"{dataFolder}/preview/{bsid}")
        log.info(f'폴더 {dataFolder}/preview/{bsid} 가 삭제되었습니다.')
        isdelpreview = 1
    except:
        pass

    #video
    try:
        shutil.rmtree(f"{dataFolder}/video/{bsid}")
        log.info(f'폴더 {dataFolder}/video/{bsid} 가 삭제되었습니다.')
        isdelvideo = 1
    except:
        pass

    #osu
    """ try:
        shutil.rmtree(f"{dataFolder}/osu/{bsid}")
        log.info(f'폴더 {dataFolder}/osu/{bsid} 가 삭제되었습니다.')
        isdelosu = 1
    except:
        pass """
    isdelosu = 0

    return {"message": {0: "Doesn't exist", 1: "Delete success"} , "osz": isdelosz, "bg": isdelbg, "thumb": isdelthumb, "audio": isdelaudio, "preview": isdelpreview, "video": isdelvideo, "osu": isdelosu}

#dbR.close()
#dbC.close()