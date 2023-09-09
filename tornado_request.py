import requests
import os
import shutil
import time

start = time.time()
bsid = 919187
url = [f"http://localhost:2/thumb/{bsid}l.jpg", f"http://localhost:2/preview/{bsid}.mp3"]
url2 = [f"https://b.redstar.moe/thumb/{bsid}l.jpg", f"https://b.redstar.moe/preview/{bsid}.mp3"]

for i in url:
    response = requests.get(i)

    if response.status_code == 200:
        data = response
        print(f"\n{data.headers}")
    else:
        print('요청 실패:', response.status_code)

end = time.time()
print(f"{end - start} Sec")