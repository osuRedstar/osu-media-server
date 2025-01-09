from functions import calculate_md5
from helpers import logUtils as log
import requests
from tqdm import tqdm

bsid = 919187
site = [f"https://catboy.best/redstar/d/{bsid}", f"https://api.nerinyan.moe/d/{bsid}", f"https://catboy.best/d/{bsid}"]
sn = ["redstar", "nerinyan", "catboy"]

for i, j in zip(site, sn):
    log.debug(f"{i} 요청 시작")
    res = requests.get(i, stream=True)
    file_size = int(res.headers.get('content-length', 185069))
    with open(f"data2/{j}_{bsid}.osz", 'wb') as file:
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, ncols=120) as pbar:
            for data in res.iter_content(1024):
                file.write(data)
                pbar.update(len(data))

oszHash = calculate_md5.file("919187 765 MILLION ALLSTARS - UNION!!.osz")
redstarHash = calculate_md5.file(f"data2/redstar_{bsid}.osz")
nerinyanHash = calculate_md5.file(f"data2/nerinyan_{bsid}.osz")
catboyHash = calculate_md5.file(f"data2/catboy_{bsid}.osz")

log.info(f"osz = {oszHash}")
log.info(f"Redstar = {redstarHash}")
log.info(f"Nerinyan = {nerinyanHash}")
log.info(f"Catboy = {catboyHash}")
