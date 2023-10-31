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

                    #temp["BeatmapID"] = filename_to_GetCheesegullDB(beatmapName)["id"]

                    # 정규식 패턴
                    pattern = r'\[([^\]]+)\]\.osu$'
                    match = re.search(pattern, beatmapName)
                    if match:
                        diffname = match.group(1)
                        sql = "SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s"
                        result = db("cheesegull").fetch(sql, (setID, diffname))
                        if result is None:
                            log.error(f"result is None | sql = {sql, (setID, diffname)}")
                            return None
                        temp["BeatmapID"] = result["id"]

                    log.info(f"{setID} 틀딱곡 cheesegull db에서 조회완료")
                    log.warning(f"{setID}/{temp['BeatmapID']} 틀딱곡 BeatmapID 세팅 완료")
                    #first_bid 선별
                    if first_bid == 0:
                        first_bid = temp["BeatmapID"]
                    elif first_bid > temp["BeatmapID"] and temp["BeatmapID"] > 0:
                        first_bid = temp["BeatmapID"]

            if "BeatmapID" in line and not underV10:
                spaceFilter = line.replace("BeatmapID:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                temp["BeatmapID"] = int(spaceFilter)

                for i in beatmap_info:
                    #중복 bid, bid <= 0
                    if int(i["BeatmapID"]) == temp["BeatmapID"] or temp["BeatmapID"] <= 0:
                        #확실하게 bid 얻기
                        #temp["BeatmapID"] = filename_to_GetCheesegullDB(beatmapName)["id"]
                        # 정규식 패턴
                        pattern = r'\[([^\]]+)\]\.osu$'
                        match = re.search(pattern, beatmapName)
                        if match:
                            diffname = match.group(1)
                            sql = "SELECT id FROM beatmaps WHERE parent_set_id = %s AND diff_name = %s"
                            result = db("cheesegull").fetch(sql, (setID, diffname))
                            if result is None:
                                log.error(f"result is None | sql = {sql}")
                                return None
                            temp["BeatmapID"] = result["id"]

                        log.error(f"{i['BeatmapID']} | .osu 파일들에서 중복 bid 감지! or .osu 파일에서 bid 값이 <= 0 임 | cheesegull db에서 bid 조회함")

                #first_bid 선별
                if first_bid == 0:
                    first_bid = temp["BeatmapID"]
                elif first_bid > temp["BeatmapID"] and temp["BeatmapID"] > 0:
                    first_bid = temp["BeatmapID"]

            elif "AudioFilename" in line and (rq_type == "audio" or rq_type == "preview"):
                spaceFilter = line.replace("AudioFilename:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                temp["AudioFilename"] = spaceFilter
            elif "PreviewTime" in line and (rq_type == "audio" or rq_type == "preview"):
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
        result = osu_file_read(setID, rq_type, moving=True)
        #필요한 파일만 각 폴더로 이동
        for item in result[2]:
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
                    except:
                        log.error(f"{setID} 비트맵셋은 audio가 없음 | no audio.mp3로 저장함")
                        shutil.copy(f"static/audio/no audio.mp3", f"data/audio/{setID}/no audio.mp3")
                
                if rq_type == "preview":
                    try:
                        shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/preview/{setID}/source_{setID}.mp3")
                        log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | preview source_{setID} 처리함")
                    except:
                        shutil.copy(f"static/audio/no audio.mp3", f"data/preview/{setID}/{setID}.mp3")
                        log.error(f"{setID} 비트맵셋은 preview가 없음 | no audio.mp3로 저장하고, preview도 처리함")

            if rq_type == "bg":
                try:
                    extension = item["BeatmapBG"][-5:][item["BeatmapBG"][-5:].find("."):]
                    shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/bg/{setID}/{item['BeatmapID']}{extension}")
                except:
                    log.error(f"{item['BeatmapID']} 비트맵은 BG가 없음 | no image.png로 저장함")
                    shutil.copy(f"static/img/no image.png", f"data/bg/{setID}/{item['BeatmapID']}.png")

            if rq_type == "audio":
                try:
                    shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/audio/{setID}/{item['AudioFilename']}")
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

            #lets | read_osu
            if rq_type.startswith("read_osu"):
                bid = int(rq_type.replace("read_osu_", ""))
                if int(item['BeatmapID']) == bid:
                    log.info(rq_type)
                    shutil.copy(f"data/dl/{setID}/{item['beatmapName']}", f"B:/redstar/lets/.data/beatmaps/{bid}.osu")
                    shutil.rmtree(f"data/dl/{setID}")
                    return 0

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

    if fullSongName == 0:
        log.warning(f"{setID} 맵셋 osz 존재하지 않음. 다운로드중...")
        
        url = [f'https://proxy.nerinyan.moe/d/{setID}', f"https://chimu.moe/d/{setID}"]
        
        limit = 0
        def dl(site, limit):
            #우선 setID .osz로 다운받고 나중에 파일 이름 변경
            file_name = f'{setID} .osz' #919187 765 MILLION ALLSTARS - UNION!!.osz, 2052147 (Love Live! series) - Colorful Dreams! Colorful Smiles! _  TV2
            save_path = 'data/dl/'  # 원하는 저장 경로로 변경
            
            # 파일 다운로드 요청
            res = requests.get(url[site], headers=requestHeaders, stream=True)
            if res.status_code == 200:
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

                log.info(f'{file_name} --> {newFilename} 다운로드 완료')
                os.rename(f"data/dl/{setID} .osz", f"data/dl/{newFilename}")
                move_files(setID, rq_type)
            else:
                log.error(f'{res.status_code}. 파일을 다운로드할 수 없습니다. chimu로 재시도!')
                limit += 1
                if limit < 3:
                    dl(1, limit)
                else:
                    log.warning(f"다운로드 요청 자체 limit 걸음! {limit}번 요청함")
        dl(0, limit=0)
    else:
        log.info(f"{get_osz_fullName(setID)} 존재함")
        move_files(setID, rq_type)

#######################################################################################################################################

def read_list():
    result = {}

    osz_file_list = [file for file in os.listdir(f"data/dl/")]
    result["osz"] = {"list": osz_file_list, "count": len(osz_file_list)}

    bg_file_list = [file for file in os.listdir(f"data/bg/")]
    result["bg"] = {"list": bg_file_list, "count": len(bg_file_list)}

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

    thumb_file_list = [file for file in os.listdir(f"data/thumb/")]
    result["thumb"] = {"list": thumb_file_list, "count": len(thumb_file_list)}

    return result

def read_bg(id):
    if "+" in id:
        id = str(id).replace("+", "")

        #bg폴더 파일 체크
        if not os.path.isdir(f"data/bg/{id}"):
            check(id, rq_type="bg")

        file_list = [file for file in os.listdir(f"data/bg/{id}") if file.startswith("+")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {id} | BG type(file_list[0]) 에러")
            check(id, rq_type="bg")
            return read_bg(f"+{id}")
        return f"data/bg/{id}/{file_list[0]}"
    else:
        bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #bg폴더 파일 체크
        if not os.path.isdir(f"data/bg/{bsid}"):
            check(bsid, rq_type="bg")

        file_list = [file for file in os.listdir(f"data/bg/{bsid}") if file.startswith(str(id))]
        try:
            type(file_list[0])
        except:
            log.error(f"bid = {id} | BG type(file_list[0]) 에러")
            check(bsid, rq_type="bg")
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
            check(bsid, rq_type="thumb")

        file_list = [file for file in os.listdir(f"data/thumb/{bsid}") if file.startswith("+")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {bsid} | thumb type(file_list[0]) 에러")
            check(bsid, rq_type="thumb")
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

        #audio폴더 파일 체크
        if not os.path.isdir(f"data/audio/{id}"):
            check(id, rq_type="audio")

        file_list = [file for file in os.listdir(f"data/audio/{id}")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {id} | audio type(file_list[0]) 에러")
            check(id, rq_type="audio")
            return read_audio(f"+{id}")
        return f"data/audio/{id}/{file_list[0]}"
    else:
        bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
        log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

        #audio폴더 파일 체크
        if not os.path.isdir(f"data/audio/{bsid}"):
           check(bsid, rq_type="audio")

        file_list = [file for file in os.listdir(f"data/audio/{bsid}")]
        try:
            #루한루프 잡자
            #type(file_list[0])
            #log.debug(type(file_list[0]))
            type(file_list[0])
        except:
            log.error(f"bid = {id} | audio type(file_list[0]) 에러")
            check(bsid, rq_type="audio")
            return read_audio(id)
        return f"data/audio/{bsid}/{file_list[0]}"

def read_preview(id):
    #source_{bsid}.mp3 먼저 확인시키기 ㄴㄴ audio에서 가져오기

    setID = id.replace(".mp3", "")
        
    if not os.path.isfile(f"data/preview/{setID}/{id}"):
        check(setID, rq_type="preview")

        #음원 하이라이트 가져오기, 밀리초라서 / 1000 함
        PreviewTime = -1
        j = osu_file_read(setID, rq_type="preview")
        #위에서 오디오 없어서 이미 처리댐
        if os.path.isfile(f"data/preview/{setID}/{id}"):
            return f"data/preview/{setID}/{id}"
        
        for i in j[2]:
            if j[1] == i["BeatmapID"]:
                PreviewTime = int(i["PreviewTime"]) / 1000
        
        ffmpeg_msg = f"ffmpeg -i data\preview\{setID}\source_{id} -ss {PreviewTime} -t 30 -acodec libmp3lame data\preview\{setID}\{id}"
        log.chat(f"ffmpeg_msg = {ffmpeg_msg}")
        os.system(ffmpeg_msg)
        os.remove(f"data/preview/{setID}/source_{id}")
    return f"data/preview/{setID}/{id}"

def read_video(id):
        bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
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
            check(bsid, rq_type="video")

        #임시로 try 박아둠, 나중에 반초라던지 비디오 있나 요청하는거로 바꾸기
        try:
            file_list = [file for file in os.listdir(f"data/video/{bsid}") if file.endswith(".mp4")]
            try:
                #log.debug(type(file_list[0]))
                type(file_list[0])
            except:
                log.error(f"bid = {id} | video type(file_list[0]) 에러")
                check(bsid, rq_type="video")
                return read_video(id)
            return f"data/video/{bsid}/{file_list[0]}"
        except:
            return "ERROR NODATA"

def read_osz(id):
    filename = get_osz_fullName(id)
    if filename != f"{id} .osz" and os.path.isfile(f"data/dl/{filename}"):
        return {"path": f"data/dl/{filename}", "filename": filename}
    else:
        check(id, rq_type="osz")
        newFilename = get_osz_fullName(id)
        if os.path.isfile(f"data/dl/{newFilename}"):
            return {"path": f"data/dl/{newFilename}", "filename": newFilename}
        else:
            return 0

def read_osz_b(id):
    bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]
    log.info(f"{id} bid cheesegull db 조회로 {bsid} bsid 얻음")

    filename = get_osz_fullName(bsid)
    if filename != f"{bsid} .osz" and os.path.isfile(f"data/dl/{filename}"):
        return {"path": f"data/dl/{filename}", "filename": filename}
    else:
        check(bsid, "osz")
        newFilename = get_osz_fullName(bsid)
        if os.path.isfile(f"data/dl/{newFilename}"):
            return {"path": f"data/dl/{newFilename}", "filename": newFilename}
        else:
            return 0

def read_osu(id):
    bsid = db("cheesegull").fetch("SELECT parent_set_id FROM cheesegull.beatmaps WHERE id = %s", (id))["parent_set_id"]

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
        check(bsid, rq_type=f"read_osu_{id}")
        return read_osu(id)
    
    if os.path.isfile(f"data/osu/{bsid}/{id}.osu"):
        return {"path": f"data/osu/{bsid}/{id}.osu", "filename": filename}
    else:
        check(bsid, rq_type=f"read_osu_{id}")
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
        log.error(f"result is None | sql = {sql}")
        return None
    return result

def read_osu_filename(filename):
    result = filename_to_GetCheesegullDB(filename)
    if result is None:
        return None
    bid = result["id"]
    return read_osu(bid)