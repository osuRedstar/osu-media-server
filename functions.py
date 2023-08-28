from lets_common_log import logUtils as log
import zipfile
import os
import shutil
import requests
from urllib.request import urlretrieve

def folder_check():
    if not os.path.isdir("dl"):
        os.mkdir("dl")
        log.info("dl 폴더 생성")
    if not os.path.isdir("audio"):
        os.mkdir("audio")
        log.info("audio 폴더 생성")
    if not os.path.isdir("preview"):
        os.mkdir("preview")
        log.info("preview 폴더 생성")
    if not os.path.isdir("thumb"):
        os.mkdir("thumb")
        log.info("thumb 폴더 생성")
    if not os.path.isdir("bg"):
        os.mkdir("bg")
        log.info("bg 폴더 생성")
    if not os.path.isdir(f"osu"):
        os.mkdir(f"osu")
        log.info("osu 폴더 생성")

def get_osz_fullName(setID):
    fullName = [file for file in os.listdir(f"dl/") if file.startswith(f"{setID} ")][0]
    return fullName

def osu_file_read(setID):
    file_list = os.listdir(f"dl/{setID}")
    file_list_osu = [file for file in file_list if file.endswith(".osu")]

    result = []
    beatmap_info = []
    # readline_all.py
    for beatmapName in file_list_osu:
        log.info(beatmapName)
        temp = {}
        bg_ignore = 0

        f = open(f"dl/{setID}/{beatmapName}", 'r', encoding="utf-8")
        while True:
            line = f.readline()
            if not line: break

            if "BeatmapID" in line:
                temp["BeatmapID"] = line.replace("BeatmapID:", "").replace("\n", "")
            elif "AudioFilename" in line:
                temp["AudioFilename"] = line.replace("AudioFilename: ", "").replace("\n", "")
            elif "PreviewTime" in line:
                temp["PreviewTime"] = line.replace("PreviewTime: ", "").replace("\n", "")
            #비트맵별 BG 파일이름
            elif ('"' and ".jpg") in line and bg_ignore == 0:
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = 1
            elif ('"' and ".png") in line and bg_ignore == 0:
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = 1
            elif ('"' and ".jpeg") in line and bg_ignore == 0:
                temp["BeatmapBG"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
                bg_ignore = 1
            #비트맵별 video 파일이름
            elif '"' and "Video" and ".mp4" in line:
                temp["BeatmapVideo"] = line[line.find('"') + 1 : line.find('"', line.find('"') + 1)]
        beatmap_info.append(temp)
        result = [setID, beatmap_info]

        #필요한 파일만 osu 폴더로 이동
        for item in result[1]:
            #아래 코드 에러 방지용 (폴더가 없으면 에러남)
            if not os.path.isdir(f"audio/{setID}"):
                os.mkdir(f"audio/{setID}")
            if not os.path.isdir(f"bg/{setID}"):
                os.mkdir(f"bg/{setID}")

            #BeatmapSetID용 미리듣기 + BG (b.redstar.moe/preview?예정)
            if item["BeatmapID"] == result[1][0]["BeatmapID"]:
                shutil.copy(f"dl/{setID}/{item['AudioFilename']}", f"audio/{setID}/-{setID}.mp3")
                shutil.copy(f"dl/{setID}/{item['BeatmapBG']}", f"bg/{setID}/-{setID}{item['BeatmapBG'][item['BeatmapBG'].find('.'):]}")

            shutil.copy(f"dl/{setID}/{item['AudioFilename']}", f"audio/{setID}/{item['BeatmapID']}.mp3")
            shutil.copy(f"dl/{setID}/{item['BeatmapBG']}", f"bg/{setID}/{item['BeatmapID']}{item['BeatmapBG'][item['BeatmapBG'].find('.'):]}")
            shutil.copy(f"dl/{setID}/{beatmapName}", f"osu/{item['BeatmapID']}.osu")

    f.close()
    shutil.rmtree(f"dl/{setID}")
    return result

def osz_unzip(setID):
    zipfile.ZipFile(f'dl/{get_osz_fullName(setID)}').extractall(f'dl/{setID}')

    log.debug(osu_file_read(setID))
    print("\n")

def check(setID):
    folder_check()
    fullSongName = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?s={setID}")
    fullSongName = fullSongName.json()[0]["artist"] + " - " + fullSongName.json()[0]["title"]
    log.debug(fullSongName)
    log.info(f"{setID} bsid Redstar API 조회로 {fullSongName} fullSongName 얻음")

    if not os.path.isfile(f"dl/{setID} {fullSongName}.osz"):
        log.warning(f"{setID} 맵셋 osz 존재하지 않음. 다운로드중...")
        
        url = f'https://proxy.nerinyan.moe/d/{setID}'
        file_name = f'{setID} {fullSongName}.osz' #919187 765 MILLION ALLSTARS - UNION!!.osz
        save_path = 'dl/'  # 원하는 저장 경로로 변경
        res = requests.get(url)
        if res.status_code == 200:
            with open(save_path + file_name, 'wb') as f:
                f.write(res.content)
            log.info(f'{file_name} 다운로드 완료')
            osz_unzip(setID)
        else:
            log.error(f'{res.status_code}. 파일을 다운로드할 수 없습니다.')
        
        #osz_unzip(setID)
    else:
        log.info(f"{get_osz_fullName(setID)} 존재함")
        osz_unzip(setID)

#######################################################################################################################################

def read_bg(id):
    if int(id) < 0:
        id = str(id).replace("-", "")

        #bg폴더 파일 체크
        if not os.path.isdir(f"bg/{id}"):
            check(id)

        file_list = [file for file in os.listdir(f"bg/{id}") if file.startswith("-")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {id} | type(file_list[0]) 에러")
            check(id)
            return read_bg(f"-{id}")
        return f"bg/{id}/{file_list[0]}"
    else:
        bsid = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}")
        bsid = bsid.json()[0]["beatmapset_id"]
        log.info(f"{id} bid Redstar API 조회로 {bsid} bsid 얻음")

        #bg폴더 파일 체크
        if not os.path.isdir(f"bg/{bsid}"):
            check(bsid)

        file_list = [file for file in os.listdir(f"bg/{bsid}") if file.startswith(str(id))]
        try:
            type(file_list[0])
        except:
            log.error(f"bid = {id} | type(file_list[0]) 에러")
            check(bsid)
            return read_bg(id)
        return f"bg/{bsid}/{file_list[0]}"
    
#osu_file_read() 역할 분할하기 (각각 따로 두기)
def read_audio(id):
    if int(id) < 0:
        id = str(id).replace("-", "")

        #audio폴더 파일 체크
        if not os.path.isdir(f"audio/{id}"):
            check(id)

        file_list = [file for file in os.listdir(f"audio/{id}") if file.startswith("-")]
        try:
            type(file_list[0])
        except:
            log.error(f"bsid = {id} | type(file_list[0]) 에러")
            check(id)
            return read_bg(f"-{id}")
        return f"audio/{id}/{file_list[0]}"
    else:
        bsid = requests.get(f"https://redstar.moe/api/v1/get_beatmaps?b={id}")
        bsid = bsid.json()[0]["beatmapset_id"]
        log.info(f"{id} bid Redstar API 조회로 {bsid} bsid 얻음")

        #bg폴더 파일 체크
        if not os.path.isdir(f"audio/{bsid}"):
            check(bsid)

        file_list = [file for file in os.listdir(f"audio/{bsid}") if file.startswith(str(id))]
        try:
            type(file_list[0])
        except:
            log.error(f"bid = {id} | type(file_list[0]) 에러")
            check(bsid)
            return read_bg(id)
        return f"audio/{bsid}/{file_list[0]}"



    setID = id.replace(".mp3", "")
    if os.path.isfile(f"audio/{setID}/-{id}"):
        return f"audio/{setID}/-{id}"
    else:
        check(setID)

def read_preview(id):
    setID = id.replace(".mp3", "")
    if os.path.isfile(f"audio/{setID}/-{id}"):
        return f"audio/{setID}/-{id}"
    else:
        check(setID)

def read_osz(id):
    if os.path.isfile(f"dl/{get_osz_fullName(id)}"):
        return f"dl/{get_osz_fullName(id)}"

def read_osu(id):
    if os.path.isfile(f"osu/{id}.osu"):
        return f"osu/{id}.osu"