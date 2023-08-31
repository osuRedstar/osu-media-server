from lets_common_log import logUtils as log
import zipfile
import os
import shutil
import requests
from urllib.request import urlretrieve
import config
from PIL import Image

conf = config.config("config.ini")

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
    if not os.path.isdir(f"data/osu"):
        os.mkdir(f"data/osu")
        log.info("data/osu 폴더 생성")

def get_osz_fullName(setID):
    try:
        fullName = [file for file in os.listdir(f"data/dl/") if file.startswith(f"{setID} ")][0]
        return fullName
    except:
        return 0

def osu_file_read(setID, moving=False):
    zipfile.ZipFile(f'data/dl/{get_osz_fullName(setID)}').extractall(f'data/dl/{setID}')

    file_list = os.listdir(f"data/dl/{setID}")
    file_list_osu = [file for file in file_list if file.endswith(".osu")]

    result = []
    beatmap_info = []
    # readline_all.py
    for beatmapName in file_list_osu:
        log.info(beatmapName)
        temp = {}
        bg_ignore = 0

        f = open(f"data/dl/{setID}/{beatmapName}", 'r', encoding="utf-8")
        while True:
            line = f.readline()
            #간혹 확장자가 대문자인 경우가 있어서 전부 소문자로 변경함
            lineCheck = line.lower()
            if not line: break

            if "BeatmapID" in line:
                spaceFilter = line.replace("BeatmapID:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                    log.warning(f"BeatmapID: 필터링 후 앞에 공백 발견되서 replace 시킴 | {spaceFilter}")
                temp["BeatmapID"] = spaceFilter
            elif "AudioFilename" in line:
                spaceFilter = line.replace("AudioFilename:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                    log.warning(f"AudioFilename: 필터링 후 앞에 공백 발견되서 replace 시킴 | {spaceFilter}")
                temp["AudioFilename"] = spaceFilter
            elif "PreviewTime" in line:
                spaceFilter = line.replace("PreviewTime:", "").replace("\n", "")
                if spaceFilter.startswith(" "):
                    spaceFilter = spaceFilter.replace(" ", "", 1)
                    log.warning(f"PreviewTime: 필터링 후 앞에 공백 발견되서 replace 시킴 | {spaceFilter}")
                temp["PreviewTime"] = spaceFilter
            #비트맵별 BG 파일이름
            elif ('"' and ".jpg") in lineCheck and bg_ignore == 0:
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = 1
            elif ('"' and ".png") in lineCheck and bg_ignore == 0:
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = 1
            elif ('"' and ".jpeg") in lineCheck and bg_ignore == 0:
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = 1
            #비트맵별 video 파일이름
            #elif '"' and "Video" and ".mp4" in line:
            elif '"' and "video" and ".mp4" in lineCheck:
                temp["BeatmapVideo"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
            temp["beatmapName"] = beatmapName

        beatmap_info.append(temp)
        result = [setID, beatmap_info]
        f.close()
    if not moving:
        shutil.rmtree(f"data/dl/{setID}")
    return result

def move_files(setID):
        result = osu_file_read(setID, moving=True)

        #필요한 파일만 각 폴더로 이동
        for item in result[1]:
            #아래 코드 에러 방지용 (폴더가 없으면 에러남)
            if not os.path.isdir(f"data/bg/{setID}"):
                os.mkdir(f"data/bg/{setID}")
                log.info(f"data/bg/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"data/thumb/{setID}"):
                os.mkdir(f"data/thumb/{setID}")
                log.info(f"data/thumb/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"data/audio/{setID}"):
                os.mkdir(f"data/audio/{setID}")
                log.info(f"data/audio/{setID} 폴더 생성 완료!")
            if not os.path.isdir(f"data/preview/{setID}"):
                os.mkdir(f"data/preview/{setID}")
                log.info(f"data/preview/{setID} 폴더 생성 완료!")
            try:
                if not os.path.isdir(f"data/video/{setID}") and item["BeatmapVideo"] is not None:
                    os.mkdir(f"data/video/{setID}")
                    log.info(f"data/video/{setID} 폴더 생성 완료!")
            except:
                log.warning(f"{item['BeatmapID']} bid no video")
                pass
            if not os.path.isdir(f"data/osu/{setID}"):
                os.mkdir(f"data/osu/{setID}")
                log.info(f"data/osu/{setID} 폴더 생성 완료!")

            log.debug(item)

            #BeatmapSetID용 미리듣기 + BG (b.redstar.moe/preview?예정)
            if item["BeatmapID"] == result[1][0]["BeatmapID"]:
                shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/bg/{setID}/+{setID}{item['BeatmapBG'][item['BeatmapBG'].find('.'):]}")
                shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/audio/{setID}/+{setID}.mp3")
                shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/preview/{setID}/source_{setID}.mp3")

            shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/bg/{setID}/{item['BeatmapID']}{item['BeatmapBG'][item['BeatmapBG'].find('.'):]}")
            shutil.copy(f"data/dl/{setID}/{item['AudioFilename']}", f"data/audio/{setID}/{item['BeatmapID']}.mp3")
            try:
                shutil.copy(f"data/dl/{setID}/{item['BeatmapVideo']}", f"data/video/{setID}/{item['BeatmapVideo']}")
            except:
                pass
            shutil.copy(f"data/dl/{setID}/{item['beatmapName']}", f"data/osu/{setID}/{item['BeatmapID']}.osu")
        #osu_file_read() 함수에 인자값으로 True를 넣어서 dl/{setID} 가 삭제 되지 않으므로 여기서 폴더 삭제함
        shutil.rmtree(f"data/dl/{setID}")

def check(setID):
    #.osz는 무조건 새로 받되, Bancho에서 ranked, loved 등등 은 새로 안받아도 댐. (Redstar에서의 랭크상태 여부는 고민중)
    #근데 생각해보니 파일 있으면 걍 이걸 안오는데?
    folder_check()
    fullSongName = get_osz_fullName(setID)
    log.debug(fullSongName)

    if fullSongName == 0:
        log.warning(f"{setID} 맵셋 osz 존재하지 않음. 다운로드중...")
        
        url = f'https://proxy.nerinyan.moe/d/{setID}'
        #우선 setID .osz로 다운받고 나중에 파일 이름 변경
        file_name = f'{setID} .osz' #919187 765 MILLION ALLSTARS - UNION!!.osz, 2052147 (Love Live! series) - Colorful Dreams! Colorful Smiles! _  TV2
        save_path = 'data/dl/'  # 원하는 저장 경로로 변경
        res = requests.get(url)
        if res.status_code == 200:
            with open(save_path + file_name, 'wb') as f:
                f.write(res.content)
            log.info(f'{file_name} --> {res.headers["filename"]} 다운로드 완료')
            os.rename(f"data/dl/{setID} .osz", f"data/dl/{res.headers['filename']}")
            move_files(setID)
        else:
            log.error(f'{res.status_code}. 파일을 다운로드할 수 없습니다.')
        
        #move_files(setID)
    else:
        log.info(f"{get_osz_fullName(setID)} 존재함")
        move_files(setID)

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

    osu_file_list = [file for file in os.listdir(f"data/osu/")]
    result["osu"] = {"list": osu_file_list, "count": len(osu_file_list)}

    thumb_file_list = [file for file in os.listdir(f"data/thumb/")]
    result["thumb"] = {"list": thumb_file_list, "count": len(thumb_file_list)}

    return result

def read_bg(id):
    if "+" in id:
        id = str(id).replace("+", "")

        #bg폴더 파일 체크
        if not os.path.isdir(f"data/bg/{id}"):
            check(id)

        file_list = [file for file in os.listdir(f"data/bg/{id}") if file.startswith("+")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {id} | type(file_list[0]) 에러")
            check(id)
            return read_bg(f"+{id}")
        return f"data/bg/{id}/{file_list[0]}"
    else:
        bsid = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}")
        bsid = bsid.json()[0]["beatmapset_id"]
        log.info(f"{id} bid Redstar API 조회로 {bsid} bsid 얻음")

        #bg폴더 파일 체크
        if not os.path.isdir(f"data/bg/{bsid}"):
            check(bsid)

        file_list = [file for file in os.listdir(f"data/bg/{bsid}") if file.startswith(str(id))]
        try:
            type(file_list[0])
        except:
            log.error(f"bid = {id} | type(file_list[0]) 에러")
            check(bsid)
            return read_bg(id)
        return f"data/bg/{bsid}/{file_list[0]}"
    
def read_thumb(id):
    bsid = id.replace("l.jpg", "")
    if os.path.isfile(f"data/thumb/{bsid}/{id}"):
        return f"data/thumb/{bsid}/{id}"
    else:
        #thumb폴더 파일 체크
        if not os.path.isdir(f"data/thumb/{id}"):
            check(bsid)

        file_list = [file for file in os.listdir(f"data/bg/{bsid}") if file.startswith("+")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {id} | type(file_list[0]) 에러")
            check(bsid)
            return read_thumb(id)

        img = Image.open(f"data/bg/{bsid}/{file_list[0]}")

        width, height = img.size
        left = (width - (height * (4 / 3))) / 2
        top = 0
        right = width - left
        bottom = height
        
        img_cropped = img.crop((left,top,right,bottom))
        img_resize = img_cropped.resize((160, 120), Image.LANCZOS)
        img_resize.save(f"data/thumb/{bsid}/{id}", quality=100)

        return f"data/thumb/{bsid}/{id}"

#osu_file_read() 역할 분할하기 (각각 따로 두기)
def read_audio(id):
    if "+" in id:
        id = str(id).replace("+", "")

        #audio폴더 파일 체크
        if not os.path.isdir(f"data/audio/{id}"):
            check(id)

        file_list = [file for file in os.listdir(f"data/audio/{id}") if file.startswith("+")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {id} | type(file_list[0]) 에러")
            check(id)
            return read_audio(f"+{id}")
        return f"data/audio/{id}/{file_list[0]}"
    else:
        bsid = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}")
        bsid = bsid.json()[0]["beatmapset_id"]
        log.info(f"{id} bid Redstar API 조회로 {bsid} bsid 얻음")

        #audio폴더 파일 체크
        if not os.path.isdir(f"data/audio/{bsid}"):
            check(bsid)

        file_list = [file for file in os.listdir(f"data/audio/{bsid}") if file.startswith(str(id))]
        try:
            #루한루프 잡자
            #type(file_list[0])
            log.debug(type(file_list[0]))
        except:
            log.error(f"bid = {id} | type(file_list[0]) 에러")
            check(bsid)
            return read_audio(id)
        return f"data/audio/{bsid}/{file_list[0]}"

def read_preview(id):
    #source_{bsid}.mp3 먼저 확인시키기 ㄴㄴ audio에서 가져오기

    setID = id.replace(".mp3", "")
        
    if not os.path.isfile(f"data/preview/{setID}/{id}"):
        check(setID)
        #음원 하이라이트 가져오기, 밀리초라서 / 1000 함
        PreviewTime = int(osu_file_read(setID)[1][0]["PreviewTime"]) / 1000
        os.system(f"ffmpeg -i data\preview\{setID}\source_{id} -ss {PreviewTime} -t 30 -acodec libmp3lame data\preview\{setID}\{id}")
        os.remove(f"data/preview/{setID}/source_{id}")
    return f"data/preview/{setID}/{id}"

def read_video(id):
        apikey = conf.config["osu"]["apikey"]
        hasVideo = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={apikey}&b={id}")
        hasVideo = hasVideo.json()[0]["video"]
        
        #type = str
        if hasVideo == "0":
            return f"{id} Beatmap has no video!"

        bsid = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}")
        bsid = bsid.json()[0]["beatmapset_id"]
        log.info(f"{id} bid Redstar API 조회로 {bsid} bsid 얻음")
        
        #video폴더 파일 체크
        if not os.path.isdir(f"data/video/{bsid}"):
            check(bsid)

        #임시로 try 박아둠, 나중에 반초라던디 비디오 있나 요청하는거로 바꾸기
        try:
            file_list = [file for file in os.listdir(f"data/video/{bsid}") if file.endswith(".mp4")]
            try:
                log.debug(type(file_list[0]))
            except:
                log.error(f"bid = {id} | type(file_list[0]) 에러")
                check(bsid)
                return read_video(id)
            return f"data/video/{bsid}/{file_list[0]}"
        except:
            return "NODATA"

def read_osz(id):
    if os.path.isfile(f"data/dl/{get_osz_fullName(id)}"):
        return {"path": f"data/dl/{get_osz_fullName(id)}", "filename": get_osz_fullName(id)}
    else:
        check(id)
        if os.path.isfile(f"data/dl/{get_osz_fullName(id)}"):
            return {"path": f"data/dl/{get_osz_fullName(id)}", "filename": get_osz_fullName(id)}
        else:
            return 0

def read_osz_b(id):
    bsid = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}")
    bsid = bsid.json()[0]["beatmapset_id"]
    log.info(f"{id} bid Redstar API 조회로 {bsid} bsid 얻음")

    if os.path.isfile(f"data/dl/{get_osz_fullName(bsid)}"):
        return {"path": f"data/dl/{get_osz_fullName(bsid)}", "filename": get_osz_fullName(bsid)}
    else:
        check(bsid)
        if os.path.isfile(f"data/dl/{get_osz_fullName(bsid)}"):
            return {"path": f"data/dl/{get_osz_fullName(bsid)}", "filename": get_osz_fullName(bsid)}
        else:
            return 0

def read_osu(id):
    bsid = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}")
    bsid = bsid.json()[0]["beatmapset_id"]
    log.info(f"{id} bid Redstar API 조회로 {bsid} bsid 얻음")

    if os.path.isfile(f"data/osu/{bsid}/{id}.osu"):
        return {"path": f"data/osu/{bsid}/{id}.osu", "filename": f"{id}.osu"}
    else:
        check(bsid)