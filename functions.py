from lets_common_log import logUtils as log
from dbConnent import db
import zipfile
import os
import shutil
import requests
from tqdm import tqdm
from urllib.request import urlretrieve
import config
from PIL import Image
import pymysql
import hashlib
import re
from mutagen.mp3 import MP3
import winsound
import threading

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

requestHeaders = {"User-Agent": "RedstarOSU's MediaServer (python request) | https://b.redstar.moe"}

conf = config.config("config.ini")

OSU_APIKEY = conf.config["osu"]["apikey"]
#lets.py 형태의 사설서버를 소유중이면 lets\.data\beatmaps 에서만 .osu 파일을 가져옴
IS_YOU_HAVE_OSU_PRIVATE_SERVER = bool(conf.config["osu"]["IS_YOU_HAVE_OSU_PRIVATE_SERVER_WITH_lets.py"])

def folder_check():
    if not os.path.isdir("data"):
        os.mkdir("data")
        log.info("data 폴더 생성")
    if not os.path.isdir("data/dl"):
        os.mkdir("data/dl")
        log.info("data/dl 폴더 생성")
    if not os.path.isdir("data/audio"):
        os.mkdir("data/audio")
        log.info("data/audio 폴더 생성")
    if not os.path.isdir("data/preview"):
        os.mkdir("data/preview")
        log.info("data/preview 폴더 생성")
    if not os.path.isdir("data/video"):
        os.mkdir("data/video")
        log.info("data/video 폴더 생성")
    if not os.path.isdir("data/thumb"):
        os.mkdir("data/thumb")
        log.info("data/thumb 폴더 생성")
    if not os.path.isdir("data/bg"):
        os.mkdir("data/bg")
        log.info("data/bg 폴더 생성")
    if not os.path.isdir(f"data/osu") and not IS_YOU_HAVE_OSU_PRIVATE_SERVER:
        os.mkdir(f"data/osu")
        log.info("data/osu 폴더 생성")

def get_osz_fullName(setID):
    try:
        fullName = [file for file in os.listdir(f"data/dl/") if file.startswith(f"{setID} ")][0]
        return fullName
    except:
        return 0

def osu_file_read(setID, rq_type, moving=False):
    zipfile.ZipFile(f'data/dl/{get_osz_fullName(setID)}').extractall(f'data/dl/{setID}')
    
    file_list = os.listdir(f"data/dl/{setID}")
    file_list_osu = [file for file in file_list if file.endswith(".osu")]

    first_bid = 0
    result = []
    beatmap_info = []
    oldMapInfo = []
    underV10 = False

    # readline_all.py
    for beatmapName in file_list_osu:
        log.info(beatmapName)
        temp = {}
        bg_ignore = False
        beatmap_md5 = calculate_md5(f"data/dl/{setID}/{beatmapName}")
        f = open(f"data/dl/{setID}/{beatmapName}", 'r', encoding="utf-8")
        while True:
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
                if int(osu_file_format_version) < 10:
                    underV10 = True
                    log.error(f"{setID} 비트맵셋의 어떤 비트맵은 시이이이이발 osu file format 이 10이하 ({osu_file_format_version}) 이네요? 시발련들아?")
                    #틀딱곡 BeatmapID 를 Version 쪽에 넘김

            if "BeatmapID:" in line and not underV10:
                spaceFilter = line.replace("BeatmapID:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                temp["BeatmapID"] = int(spaceFilter)

                # 정규식 패턴
                pattern = r'\[([^\]]+)\]\.osu$'
                match = re.search(pattern, beatmapName)
                RealBid = {"id": temp["BeatmapID"]}
                if match:
                    diffname = match.group(1)
                    sql = "SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s"
                    # windows 특수문자 이슈
                    if diffname != temp["Version"] and temp["Version"] != "":
                        log.error(f"diffname 매치 안됨! .osu안의 결과물 사용! | diffname = {diffname} | temp['Version'] = {temp['Version']}")
                        RealBid = db("cheesegull").fetch(sql, (setID, temp["Version"]))
                    else:
                        RealBid = db("cheesegull").fetch(sql, (setID, diffname))

                    if RealBid is None or type(RealBid) is list:
                        log.warning(f"Realbid = {RealBid} | RealBid가 cheesegull에서 조회되지 않음! 스킵함")
                        RealBid = {"id": temp["BeatmapID"]}

                #중?복 bid, bid <= 0 감지
                if temp["BeatmapID"] != RealBid["id"] or temp["BeatmapID"] <= 0:
                    log.error(f"{temp['BeatmapID']} --> {RealBid['id']} | .osu 파일들에서 중복 bid 감지! or .osu 파일에서 bid 값이 <= 0 임 | cheesegull db에서 bid 조회함")
                    temp["BeatmapID"] = RealBid["id"]

                #first_bid 선별
                if first_bid == 0 and temp["BeatmapID"] > 0:
                    first_bid = temp["BeatmapID"]
                elif first_bid > temp["BeatmapID"] and temp["BeatmapID"] > 0:
                    first_bid = temp["BeatmapID"]

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
                            result = db("cheesegull").fetch(sql, (setID, temp["Version"]))
                        else:
                            result = db("cheesegull").fetch(sql, (setID, diffname))

                        if result is None:
                            return None
                        temp["BeatmapID"] = result["id"]

                    log.info(f"{setID} 틀딱곡 cheesegull db에서 조회완료")
                    log.warning(f"{setID}/{temp['BeatmapID']} 틀딱곡 BeatmapID 세팅 완료")
                    #first_bid 선별
                    if first_bid == 0:
                        first_bid = temp["BeatmapID"]
                    elif first_bid > temp["BeatmapID"] and temp["BeatmapID"] > 0:
                        first_bid = temp["BeatmapID"]
            elif "AudioFilename:" in line and (rq_type == "audio" or rq_type == "preview"):
                spaceFilter = line.replace("AudioFilename:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                temp["AudioFilename"] = spaceFilter
            elif "PreviewTime:" in line and (rq_type == "audio" or rq_type == "preview"):
                spaceFilter = line.replace("PreviewTime:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                temp["PreviewTime"] = spaceFilter
            #비트맵별 BG 파일이름
            elif ('"' and ".jpg") in lineCheck and not bg_ignore and (rq_type == "bg" or rq_type == "thumb"):
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = True
            elif ('"' and ".png") in lineCheck and not bg_ignore and (rq_type == "bg" or rq_type == "thumb"):
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = True
            elif ('"' and ".jpeg") in lineCheck and not bg_ignore and (rq_type == "bg" or rq_type == "thumb"):
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = True
            #비트맵별 video 파일이름
            #.avi 추가하기
            #elif '"' and "Video" and ".mp4" in line:
            elif '"' and "video" and ".mp4" in lineCheck and rq_type == "video":
                temp["BeatmapVideo"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
            elif '"' and ".mp4" in lineCheck and rq_type == "video" and underV10:
                temp["BeatmapVideo"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
            temp["beatmapName"] = beatmapName

        beatmap_info.append(temp)
        f.close()

    log.debug(f"first_bid = {first_bid}")
    result = [setID, first_bid, beatmap_info]
    if not moving:
        shutil.rmtree(f"data/dl/{setID}")
    return result

def move_files(setID, rq_type):
        isOsuFile = False
        result = osu_file_read(setID, rq_type, moving=True)
        #필요한 파일만 각 폴더로 이동
        for item in result[2]:
            isOsuFile = True
            #아래 코드 에러 방지용 (폴더가 없으면 에러남)
            if not os.path.isdir(f"data/bg/{setID}") and rq_type == "bg":
                os.mkdir(f"data/bg/{setID}")
                log.info(f"data/bg/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"data/thumb/{setID}") and rq_type == "thumb":
                os.mkdir(f"data/thumb/{setID}")
                log.info(f"data/thumb/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"data/audio/{setID}") and rq_type == "audio":
                os.mkdir(f"data/audio/{setID}")
                log.info(f"data/audio/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"data/preview/{setID}") and rq_type == "preview":
                os.mkdir(f"data/preview/{setID}")
                log.info(f"data/preview/{setID} 폴더 생성 완료!")
            try:
                if not os.path.isdir(f"data/video/{setID}") and item["BeatmapVideo"] is not None and rq_type == "video":
                    os.mkdir(f"data/video/{setID}")
                    log.info(f"data/video/{setID} 폴더 생성 완료!")
            except:
                #log.warning(f"{item['BeatmapID']} bid no video")
                pass
            if not os.path.isdir(f"data/osu/{setID}") and not IS_YOU_HAVE_OSU_PRIVATE_SERVER and rq_type == "osu":
                os.mkdir(f"data/osu/{setID}")
                log.info(f"data/osu/{setID} 폴더 생성 완료!")

            #log.debug(item)

            #BeatmapSetID용 미리듣기 + BG (b.redstar.moe/preview?예정)
            #if item["BeatmapID"] == result[2][0]["BeatmapID"]:
            if item["BeatmapID"] == result[1]:
                if rq_type == "bg":
                    try:
                        extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                        shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/bg/{setID}/+{setID}{extension}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | BG 처리함")
                    except:
                        log.error(f"{setID} 비트맵셋은 BG가 없음 | no image.png로 저장함")
                        shutil.copy(f"static/img/no image.png", f"data/bg/{setID}/+{setID}.png")

                if rq_type == "thumb":
                    try:
                        extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                        shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/thumb/{setID}/+{setID}{extension}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | thumb 처리함")
                    except:
                        log.error(f"{setID} 비트맵셋은 thumb가 없음 | no image.png로 저장함")
                        shutil.copy(f"static/img/no image.png", f"data/thumb/{setID}/+{setID}.png")

                if rq_type == "audio":
                    try:
                        shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/audio/{setID}/{item['AudioFilename']}")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | audio 처리함")
                    except:
                        log.error(f"{setID} 비트맵셋은 audio가 없음 | no audio.mp3로 저장함")
                        shutil.copy(f"static/audio/no audio.mp3", f"data/audio/{setID}/no audio.mp3")
                
                if rq_type == "preview":
                    try:
                        shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/preview/{setID}/source_{setID}.mp3")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | preview source_{setID} 처리함")
                    except:
                        shutil.copy(f"static/audio/no audio.mp3", f"data/preview/{setID}/no audio_{setID}.mp3")
                        log.error(f"{setID} 비트맵셋은 preview가 없음 | no audio.mp3로 저장하고, preview도 처리함")

            if rq_type == "bg":
                try:
                    extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                    shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/bg/{setID}/{item['BeatmapID']}{extension}")
                    log.info(f"{item['BeatmapID']} 비트맵 | BG 처리함")
                except:
                    log.error(f"{item['BeatmapID']} 비트맵은 BG가 없음 | no image.png로 저장함")
                    shutil.copy(f"static/img/no image.png", f"data/bg/{setID}/{item['BeatmapID']}.png")

            if rq_type == "audio":
                try:
                    shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/audio/{setID}/{item['AudioFilename']}")
                    log.info(f"{item['BeatmapID']} 비트맵 | audio 처리함")
                except:
                    log.error(f"{item['BeatmapID']} 비트맵은 audio가 없음 | no audio.mp3로 저장함")
                    shutil.copy(f"static/audio/no audio.mp3", f"data/audio/{setID}/no audio.mp3")

            if rq_type == "video":
                try:
                    shutil.copy(f"data/dl/{setID}/{item['BeatmapVideo']}", f"data/video/{setID}/{item['BeatmapVideo']}")
                    log.info(f"{item['BeatmapID']} 비트맵은 video가 존재함!")
                except:
                    pass
            
            if not IS_YOU_HAVE_OSU_PRIVATE_SERVER and rq_type == "osu":
                shutil.copy(f"data/dl/{setID}/{item['beatmapName']}", f"data/osu/{setID}/{item['BeatmapID']}.osu")
                log.info(f"{item['BeatmapID']} 비트맵 | osu 처리함")

            #lets | read_osu
            if rq_type.startswith("read_osu"):
                bid = int(rq_type.replace("read_osu_", ""))
                if int(item['BeatmapID']) == bid:
                    log.info(rq_type)
                    shutil.copy(f"data/dl/{setID}/{item['beatmapName']}", f"B:/redstar/lets/.data/beatmaps/{bid}.osu")
                    log.info(f"{bid}.osu | lets에 넣음")
                    shutil.rmtree(f"data/dl/{setID}")
                    return 0

        if not isOsuFile:
            raise FileNotFoundError(f".osu 파일이 존재하지 않는것으로 보임! | [WinError 3] 지정된 경로를 찾을 수 없습니다: 'data/{rq_type}/{setID}'")

        #osu_file_read() 함수에 인자값으로 True를 넣어서 dl/{setID} 가 삭제 되지 않으므로 여기서 폴더 삭제함
        shutil.rmtree(f"data/dl/{setID}")

def check(setID, rq_type):
    #.osz는 무조건 새로 받되, Bancho, Redstar**전용** 맵에서 ranked, loved 등등 은 새로 안받아도 댐. (Redstar에서의 랭크상태 여부는 고민중)
    #근데 생각해보니 파일 있으면 걍 이걸 안오는데?
    folder_check()
    fullSongName = get_osz_fullName(setID)
    log.debug(fullSongName)

    if fullSongName == f"{setID} .osz":
        log.error(f"{fullSongName} | 존재는 하나 꺠지거나 문제가 있음. 재 다운로드중...")
        fullSongName = 0

    url = [f'https://api.nerinyan.moe/d/{setID}', f"https://chimu.moe/d/{setID}"]

    if fullSongName == 0:
        log.warning(f"{setID} 맵셋 osz 존재하지 않음. 다운로드중...")
        
        limit = 0
        def dl(site, limit):
            #우선 setID .osz로 다운받고 나중에 파일 이름 변경
            file_name = f'{setID} .osz' #919187 765 MILLION ALLSTARS - UNION!!.osz, 2052147 (Love Live! series) - Colorful Dreams! Colorful Smiles! _  TV2
            save_path = 'data/dl/'  # 원하는 저장 경로로 변경
            
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
                    winsound.PlaySound("static/audio/match-confirm (mp3cut.net).wav", winsound.SND_FILENAME)
                play_thread = threading.Thread(target=play_finished_dl)
                play_thread.start()

                os.rename(f"data/dl/{setID} .osz", f"data/dl/{newFilename}")
                move_files(setID, rq_type)
            else:
                log.error(f'{statusCode}. 파일을 다운로드할 수 없습니다. chimu로 재시도!')
                limit += 1
                if limit < 3:
                    return dl(1, limit)
                else:
                    log.warning(f"다운로드 요청 자체 limit 걸음! {limit}번 요청함")
                    return statusCode
        return dl(0, limit=0)
    else:
        """ exceptOszList = [919187, 871223, 12483, 1197242]

        #이거 redstar DB에 없는 경우 있으니 cheesegull DB에서도 추가로 참고하기
        rankStatus = db("redstar").fetch(f"SELECT ranked FROM beatmaps WHERE beatmapset_id = %s", (setID))["ranked"]
        if rankStatus <= 0 and setID not in exceptOszList:
            oszHash = calculate_md5(f"data/dl/{fullSongName}")
            log.debug(f"oszHash = {oszHash}")
            for i in url:
                newOszHash = requests.get(i, headers=requestHeaders, timeout=5)
                if newOszHash.status_code == 200:
                    with open(f"data/dl/{setID}t .osz", 'wb') as file:
                        file.write(newOszHash.content)
                    newOszHash = calculate_md5(f"data/dl/{fullSongName}")
                    log.debug(f"newOszHash = {newOszHash}")
                    if oszHash != newOszHash:
                        log.warning(f"{setID} 가 최신이 아닙니다!")
                        return dl(0, limit=0)
                    else:
                        break
                else:
                    continue """

        log.info(f"{get_osz_fullName(setID)} 존재함")
        try:
            move_files(setID, rq_type)
        except Exception as e:
            return e

#######################################################################################################################################

def read_list():
    result = {}

    osz_file_list = [file for file in os.listdir(f"data/dl/")]
    result["osz"] = {"list": osz_file_list, "count": len(osz_file_list)}

    bg_file_list = [file for file in os.listdir(f"data/bg/")]
    result["bg"] = {"list": bg_file_list, "count": len(bg_file_list)}

    thumb_file_list = [file for file in os.listdir(f"data/thumb/")]
    result["thumb"] = {"list": thumb_file_list, "count": len(thumb_file_list)}

    audio_file_list = [file for file in os.listdir(f"data/audio/")]
    result["audio"] = {"list": audio_file_list, "count": len(audio_file_list)}

    preview_file_list = [file for file in os.listdir(f"data/preview/")]
    result["preview"] = {"list": preview_file_list, "count": len(preview_file_list)}

    video_file_list = [file for file in os.listdir(f"data/video/")]
    result["video"] = {"list": video_file_list, "count": len(video_file_list)}

    try:
        osu_file_list = [file for file in os.listdir(f"data/osu/")]
        result["osu"] = {"list": osu_file_list, "count": len(osu_file_list)}
    except:
        result["osu"] = {"list": "NO FOLDER", "count": 0}

    return result

def read_bg(id):
    if "+" in id:
        id = str(id).replace("+", "")

        #bg폴더 파일 체크
        if not os.path.isdir(f"data/bg/{id}"):
            #파일 다운로드시에 500 뜨면 500 코드로 반환 예정, 만약 우리서버 문제면 main.py 에서 503 코드로 반환
            ck = check(id, rq_type="bg")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"data/bg/{id}") if file.startswith("+")]
        try:
            print(file_list[0])
        except:
            log.error(f"bsid = {id} | BG print(file_list[0]) 에러")
            ck = check(id, rq_type="bg")
            if ck is not None:
                return ck
            return read_bg(f"+{id}")
        return f"data/bg/{id}/{file_list[0]}"
    else:
        try:
            bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
        except:
            try:
                bsid = int(requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}").json()[0]["beatmapset_id"])
                log.info("RedstarOSU API에서 bsid 찾음")
            except:
                raise KeyError("Not Found bsid!")

        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #bg폴더 파일 체크
        if not os.path.isdir(f"data/bg/{bsid}"):
            ck = check(bsid, rq_type="bg")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"data/bg/{bsid}") if file.startswith(str(id))]
        try:
            print(file_list[0])
        except:
            log.error(f"bid = {id} | BG print(file_list[0]) 에러")
            ck = check(bsid, rq_type="bg")
            if ck is not None:
                return ck
            return read_bg(id)
        return f"data/bg/{bsid}/{file_list[0]}"
    
def read_thumb(id):
    if "l.jpg" in id:
        bsid = id.replace("l.jpg", "")
        img_size = (160, 120)
    else:
        bsid = id.replace(".jpg", "")
        img_size = (80, 60)

    if os.path.isfile(f"data/thumb/{bsid}/{id}"):
        return f"data/thumb/{bsid}/{id}"
    else:
        #thumb폴더 파일 체크
        if not os.path.isdir(f"data/thumb/{bsid}"):
            ck = check(bsid, rq_type="thumb")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"data/thumb/{bsid}") if file.startswith("+")]
        try:
            print(file_list[0])
        except:
            log.error(f"bsid = {bsid} | thumb print(file_list[0]) 에러")
            ck = check(bsid, rq_type="thumb")
            if ck is not None:
                return ck
            return read_thumb(id)

        img = Image.open(f"data/thumb/{bsid}/{file_list[0]}")
        # 이미지 모드를 RGBA에서 RGB로 변환
        img = img.convert("RGB")

        width, height = img.size
        left = (width - (height * (4 / 3))) / 2
        top = 0
        right = width - left
        bottom = height
        
        img_cropped = img.crop((left,top,right,bottom))
        img_resize = img_cropped.resize(img_size, Image.LANCZOS)
        img_resize.save(f"data/thumb/{bsid}/{id}", quality=100)

        os.remove(f"data/thumb/{bsid}/{file_list[0]}")

        return f"data/thumb/{bsid}/{id}"

#osu_file_read() 역할 분할하기 (각각 따로 두기)
def read_audio(id):
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

        #audio폴더 파일 체크
        if not os.path.isdir(f"data/audio/{id}"):
            check(id, rq_type="audio")

        file_list = [file for file in os.listdir(f"data/audio/{id}")]

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
            return read_audio(f"+{id}")

        if mods == "DT":
            DTFilename = f"data/audio/{id}/{file_list[0][:-4]}-DT.mp3"
            if os.path.isfile(DTFilename):
                return DTFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "data\\audio\{id}\{file_list[0]}" -af atempo=1.5 -y "data\\audio\{id}\{file_list[0][:-4]}-DT.mp3"'
                log.chat(f"DT ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return DTFilename
        elif mods == "NC":
            NCFilename = f"data/audio/{id}/{file_list[0][:-4]}-NC.mp3"
            if os.path.isfile(NCFilename):
                return NCFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "data\\audio\{id}\{file_list[0]}" -af asetrate={MP3(f"data/audio/{id}/{file_list[0]}").info.sample_rate}*1.5 -y "data\\audio\{id}\{file_list[0][:-4]}-NC.mp3"'
                log.chat(f"NC ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return NCFilename
        elif mods == "HF":
            HFFilename = f"data/audio/{id}/{file_list[0][:-4]}-HF.mp3"
            if os.path.isfile(HFFilename):
                return HFFilename
            else:
                ffmpeg_msg = f'ffmpeg -i "data\\audio\{id}\{file_list[0]}" -af atempo=0.75 -y "data\\audio\{id}\{file_list[0][:-4]}-HF.mp3"'
                log.chat(f"HF ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return HFFilename
        else:
            return f"data/audio/{id}/{file_list[0]}"
    
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

        try:
            bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
        except:
            try:
                bsid = int(requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}").json()[0]["beatmapset_id"])
                log.info("RedstarOSU API에서 bsid 찾음")
            except:
                raise KeyError("Not Found bsid!")

        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #audio폴더 파일 체크
        if not os.path.isdir(f"data/audio/{bsid}"):
            ck = check(bsid, rq_type="audio")
            if ck is not None:
                return ck

        file_list = [file for file in os.listdir(f"data/audio/{bsid}")]

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
            return read_audio(id)
        
        if mods == "DT":
            DTFilename = f"data/audio/{bsid}/{file_list[0][:-4]}-DT.mp3"
            if os.path.isfile(DTFilename):
                return DTFilename
            else:
                ffmpeg_msg = f'ffmpeg -i data\\audio\{bsid}\{file_list[0]} -af atempo=1.5 -y data\\audio\{bsid}\{file_list[0][:-4]}-DT.mp3'
                log.chat(f"DT ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return DTFilename
        elif mods == "NC":
            NCFilename = f"data/audio/{bsid}/{file_list[0][:-4]}-NC.mp3"
            if os.path.isfile(NCFilename):
                return NCFilename
            else:
                ffmpeg_msg = f'ffmpeg -i data\\audio\{bsid}\{file_list[0]} -af asetrate={MP3(f"data/audio/{bsid}/{file_list[0]}").info.sample_rate}*1.5 -y data\\audio\{bsid}\{file_list[0][:-4]}-NC.mp3'
                log.chat(f"NC ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return NCFilename
        elif mods == "HF":
            HFFilename = f"data/audio/{bsid}/{file_list[0][:-4]}-HF.mp3"
            if os.path.isfile(HFFilename):
                return HFFilename
            else:
                ffmpeg_msg = f'ffmpeg -i data\\audio\{bsid}\{file_list[0]} -af atempo=0.75 -y data\\audio\{bsid}\{file_list[0][:-4]}-HF.mp3'
                log.chat(f"HF ffmpeg_msg = {ffmpeg_msg}")
                os.system(ffmpeg_msg)
                return HFFilename
        else:
            return f"data/audio/{bsid}/{file_list[0]}"

def read_preview(id):
    #source_{bsid}.mp3 먼저 확인시키기 ㄴㄴ audio에서 가져오기

    setID = id.replace(".mp3", "")
        
    if not os.path.isfile(f"data/preview/{setID}/{id}"):
        if os.path.isfile(f"data/preview/{setID}/no audio_{id}"):
            #위에서 오디오 없어서 이미 처리댐 (no audio.mp3)
            log.warning(f"no audio_{id}")
            return f"data/preview/{setID}/no audio_{id}"

        ck = check(setID, rq_type="preview")
        if ck is not None:
            return ck

        #음원 하이라이트 가져오기, 밀리초라서 / 1000 함
        PreviewTime = -1
        j = osu_file_read(setID, rq_type="preview")
        
        for i in j[2]:
            if j[1] == i["BeatmapID"]:
                prti = int(i["PreviewTime"])
                if prti == -1:
                    audio = MP3(f"data/preview/{setID}/source_{id}")
                    PreviewTime = audio.info.length / 2.5
                    log.warning(f"{setID}.mp3 (source_{id}) 의 PreviewTime 값이 {prti} 이므로 TotalLength / 2.5 == {PreviewTime} 로 세팅함")
                else:
                    PreviewTime = prti / 1000
        
        ffmpeg_msg = f"ffmpeg -i data\preview\{setID}\source_{id} -ss {PreviewTime} -t 30.821 -acodec copy -y data\preview\{setID}\{id}"
        log.chat(f"ffmpeg_msg = {ffmpeg_msg}")
        os.system(ffmpeg_msg)
        os.remove(f"data/preview/{setID}/source_{id}")
    return f"data/preview/{setID}/{id}"

def read_video(id):
        try:
            bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
        except:
            try:
                bsid = int(requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}").json()[0]["beatmapset_id"])
                log.info("RedstarOSU API에서 bsid 찾음")
            except:
                raise KeyError("Not Found bsid!")

        try:
            #hasVideo = db("cheesegull").fetch("SELECT has_video FROM cheesegull.sets WHERE id = %s", (bsid))["has_video"]
            #반초로 조회함
            hasVideo = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_APIKEY}&b={id}", headers=requestHeaders)
            hasVideo = hasVideo.json()[0]["video"]
        except:
            try:
                log.warning(f"{id} 해당 비트맵은 반초 API에서 조회가 되지 않습니다! | .osu 파일에 비디오 있나 체크")
                log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
                ismp4 = osu_file_read(bsid, rq_type="video")
                #사실 의미 없음
                hasVideo = ismp4[2][0]["BeatmapVideo"]
            except:
                log.error(f"{id} 해당 비트맵은 .osu 파일에서도 mp4가 발견되지 않음")
                return f"{id} Beatmap doesn't exist on Bancho API!"
            
        #type = str --> type = int
        if hasVideo == 0:
            return f"{id} Beatmap has no video!"
        
        #video폴더 파일 체크
        if not os.path.isdir(f"data/video/{bsid}"):
            ck = check(bsid, rq_type="video")
            if ck is not None:
                return ck

        #임시로 try 박아둠, 나중에 반초라던지 비디오 있나 요청하는거로 바꾸기
        try:
            file_list = [file for file in os.listdir(f"data/video/{bsid}") if file.endswith(".mp4")]

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
            return f"data/video/{bsid}/{file_list[0]}"
        except:
            return "ERROR NODATA"

def read_osz(id):
    filename = get_osz_fullName(id)
    if filename != f"{id} .osz" and os.path.isfile(f"data/dl/{filename}"):
        return {"path": f"data/dl/{filename}", "filename": filename}
    else:
        ck = check(id, rq_type="osz")
        if ck is not None:
            return ck
        newFilename = get_osz_fullName(id)
        if os.path.isfile(f"data/dl/{newFilename}"):
            return {"path": f"data/dl/{newFilename}", "filename": newFilename}
        else:
            return 0

def read_osz_b(id):
    try:
        bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
    except:
        try:
            bsid = int(requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}").json()[0]["beatmapset_id"])
            log.info("RedstarOSU API에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")
    return read_osz(bsid)

def read_osu(id):
    try:
        bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
    except:
        try:
            bsid = int(requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}").json()[0]["beatmapset_id"])
            log.info("RedstarOSU API에서 bsid 찾음")
        except:
            raise KeyError("Not Found bsid!")

    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

    #B:\redstar\lets\.data\beatmaps 우선시함
    if os.path.isfile(f"B:/redstar/lets/.data/beatmaps/{id}.osu"):
        log.info(f"{id}.osu 파일을 B:/redstar/lets/.data/beatmaps/{id}.osu에서 먼저 찾아서 반환함")
        
        sql = '''
            SELECT CONCAT(s.artist, ' - ', s.title, ' (', s.creator, ') [', b.diff_name, ']' '.osu') AS filename
            FROM sets AS s
            JOIN beatmaps AS b ON s.id = b.parent_set_id
            WHERE b.id = %s
        '''
        filename = db("cheesegull").fetch(sql, (id))
        log.debug(filename)
        if filename is None:
            log.error(f"filename is None | sql = {sql}")
            return None
        return {"path": f"B:/redstar/lets/.data/beatmaps/{id}.osu", "filename": filename["filename"]}
    else:
        ck = check(bsid, rq_type=f"read_osu_{id}")
        if ck is not None:
            return ck
        return read_osu(id)
    
    if os.path.isfile(f"data/osu/{bsid}/{id}.osu"):
        return {"path": f"data/osu/{bsid}/{id}.osu", "filename": filename}
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
        else:
            # 정규식 패턴
            pattern = r"^(.+) - (.+) (\([^()]+\)) \(([^()]+)\) \[([^]]+)\]\.osu$"
            match = re.match(pattern, filename)

            artist = match.group(1)
            title = f"{match.group(2)} {match.group(3)}"
            creator = match.group(4)
            version = match.group(5)
    except:
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
    result = db("cheesegull").fetch(sql, (artist, title, creator, version))
    if result is None:
        return None
    return result

def read_osu_filename(filename):
    result = filename_to_GetCheesegullDB(filename)
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
            os.remove(f"data/dl/{osz}")
            log.info(f'파일 {osz} 가 삭제되었습니다.')
            isdelosz = 1
        except OSError as e:
            log.error(f'파일 삭제 실패: {e}')
    try:
        shutil.rmtree(f"data/dl/{bsid}")
        log.info(f'폴더 data/dl/{bsid} 가 삭제되었습니다.')
    except:
        pass

    #bg
    try:
        shutil.rmtree(f"data/bg/{bsid}")
        log.info(f'폴더 data/bg/{bsid} 가 삭제되었습니다.')
        isdelbg = 1
    except:
        pass

    #thumb
    try:
        shutil.rmtree(f"data/thumb/{bsid}")
        log.info(f'폴더 data/thumb/{bsid} 가 삭제되었습니다.')
        isdelthumb = 1
    except:
        pass

    #audio
    try:
        shutil.rmtree(f"data/audio/{bsid}")
        log.info(f'폴더 data/audio/{bsid} 가 삭제되었습니다.')
        isdelaudio = 1
    except:
        pass

    #preview
    try:
        shutil.rmtree(f"data/preview/{bsid}")
        log.info(f'폴더 data/preview/{bsid} 가 삭제되었습니다.')
        isdelpreview = 1
    except:
        pass

    #video
    try:
        shutil.rmtree(f"data/video/{bsid}")
        log.info(f'폴더 data/video/{bsid} 가 삭제되었습니다.')
        isdelvideo = 1
    except:
        pass

    #osu
    """ try:
        shutil.rmtree(f"data/osu/{bsid}")
        log.info(f'폴더 data/osu/{bsid} 가 삭제되었습니다.')
        isdelosu = 1
    except:
        pass """
    isdelosu = 0

    return {"message": {0: "Doesn't exist", 1: "Delete success"} , "osz": isdelosz, "bg": isdelbg, "thumb": isdelthumb, "audio": isdelaudio, "preview": isdelpreview, "video": isdelvideo, "osu": isdelosu}






