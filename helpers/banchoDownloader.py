import zipfile, os, psutil, shutil, requests, re, time, json, traceback, threading
from helpers import config, logUtils as log
from tqdm import tqdm

def exceptionE(msg=""): e = traceback.format_exc(); log.error(f"{msg} \n{e}"); return e

conf = config.config("config.ini")
bancho_username = conf.config["osu"]["bancho_username"]
bancho_password = conf.config["osu"]["bancho_password"]
dataFolder = conf.config["server"]["dataFolder"]
osuServerDomain = conf.config["server"]["osuServerDomain"]

requestHeaders = {"User-Agent": f"RedstarOSU's MediaServer (python requests) | https://b.{osuServerDomain}"}
OSisWindows = os.name == "nt"

# 토큰을 메모리에 들고 있기 위한 전역 변수
access_token = {}
token_expires_at = 0

def getToken(n: str = None, p: str = None) -> dict:
    try:
        global access_token, token_expires_at
        if access_token and time.time() < token_expires_at: return access_token
        data = {
            "username": bancho_username if not n else n,
            "password": bancho_password if not p else p,
            "grant_type": "password",
            "client_id": "5", #osu!lazer Client
            "client_secret": "FGc9GAtyHzeQDshWP5Ah7dega8hJACAJpQtw6OXk", #osu!lazer Client
            "scope": "*"
        }
        res = None; res = requests.post("https://osu.ppy.sh/oauth/token", data=data, headers={"User-Agent": "osu!"}, timeout=5)
        token = res.json()
        token_expires_at = token['token_expires_at'] = time.time() + token['expires_in'] - 60 #보통 토큰 유효기간은 하루(86400초)입니다. 안전하게 만료 60초 전으로 세팅합니다.
        token["username"] = data["username"]
        if not n and not p: access_token = token
    except: token = 500 if not res else res.status_code
    return token

def download(setID: int, token: dict = None) -> list:
    if token and type(token) == int:
        log.error(f"{token} | token 값 오류! {bancho_username} 의 정보로 재시도"); token = getToken()
    elif not token: token = getToken()
    if type(token) != dict:
        log.error(f"{token} | token 값 오류로 {token} 반환함"); return token

    file_name = f'{setID} .osz'; save_path = f'{dataFolder}/dl/'
    link = f"https://osu.ppy.sh/api/v2/beatmapsets/{setID}/download"
    headers = {"Authorization": f"{token['token_type']} {token['access_token']}"}

    # 파일 다운로드 요청
    try:
        res = requests.get(link, headers={**headers, **requestHeaders}, timeout=5, stream=True)
        statusCode = res.status_code
        header_filename = res.headers.get('Content-Disposition')
    except requests.exceptions.ReadTimeout as e:
        log.warning(f"{link} Timeout! | e = {e}")
        statusCode = 504
    except:
        statusCode = res.status_code if res.status_code != 200 else 500
        exceptionE(f"{statusCode} | 파일다운 기본 예외처리 | url = {link}")

    if statusCode == 200 and header_filename:
        file_size = int(res.headers.get('Content-Length', 0)) #파일 크기를 얻습니다.

        # tqdm을 사용하여 진행률 표시
        with open(save_path + file_name, 'wb') as file:
            with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, ncols=120, desc=f"Bancho API v2 ({setID})") as pbar:
                for data in res.iter_content(1024):
                    file.write(data)
                    pbar.update(len(data))

        newFilename = re.findall('filename="([^"]+)"', header_filename)[0]
        if "%20" in newFilename: newFilename = newFilename.replace("%20", " ")
        newFilename = re.sub(r'[<>:"/\\|?*]', '_', newFilename)

        log.info(f'{file_name} --> {newFilename} 다운로드 완료')

        def play_finished_dl(): #WAV 파일 재생을 별도의 스레드에서 수행
            os.system(f"ffplay -nodisp -autoexit static/audio/match-confirm.mp3 > {'nul' if OSisWindows else '/dev/null'} 2>&1")
        play_thread = threading.Thread(target=play_finished_dl)
        play_thread.start()

        try: os.rename(f"{dataFolder}/dl/{setID} .osz", f"{dataFolder}/dl/{newFilename}")
        except FileExistsError:
            ct = int(os.stat(f"{dataFolder}/dl/{newFilename}").st_ctime)
            shutil.copy2(f"{dataFolder}/dl/{newFilename}", f"{dataFolder}/dl-old/{newFilename[:-4]}-{ct}~{int(time.time())}.osz")
            os.remove(f"{dataFolder}/dl/{newFilename}")
            os.replace(f"{dataFolder}/dl/{setID} .osz", f"{dataFolder}/dl/{newFilename}")
        return statusCode

    return statusCode