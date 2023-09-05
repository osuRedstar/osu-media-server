import requests

bsid = 919187
url = [f"http://localhost:2/thumb/{bsid}l.jpg", f"http://localhost:2/preview/{bsid}.mp3"]
url2 = [f"https://b.redstar.moe/thumb/{bsid}l.jpg", f"https://b.redstar.moe/preview/{bsid}.mp3"]

for i in url:
    response = requests.get(i)

    if response.status_code == 200:
        data = response
        print(data)
    else:
        print('요청 실패:', response.status_code)







def move_files(setID):
        result = osu_file_read(setID, moving=True)
        #필요한 파일만 각 폴더로 이동
        for item in result[2]:
            #아래 코드 에러 방지용 (폴더가 없으면 에러남)
            if not os.path.isdir(f"data/bg/{setID}"):
                os.mkdir(f"data/bg/{setID}")
                log.info(f"data/bg/{setID} 폴더 생성 완료!")

            #BeatmapSetID용 미리듣기 + BG (b.redstar.moe/preview?예정)
            #if item["BeatmapID"] == result[2][0]["BeatmapID"]:
            if item["BeatmapID"] == result[1]:
                try:
                    shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/bg/{setID}/+{setID}{item['BeatmapBG'][item['BeatmapBG'].find('.'):]}")
                    log.info(f"{setID} 비트맵셋, {item['BeatmapID']} 비트맵 | BG 처리함")
                except:
                    log.error(f"{setID} 비트맵셋은 BG가 없음 | no image.png로 저장함")
                    shutil.copy(f"static/img/no image.png", f"data/bg/{setID}/+{setID}.png")

            try:
                shutil.copy(f"data/dl/{setID}/{item['BeatmapBG']}", f"data/bg/{setID}/{item['BeatmapID']}{item['BeatmapBG'][item['BeatmapBG'].find('.'):]}")
            except:
                log.error(f"{item['BeatmapID']} 비트맵은 BG가 없음 | no image.png로 저장함")
                shutil.copy(f"static/img/no image.png", f"data/bg/{setID}/{item['BeatmapID']}.png")

        #osu_file_read() 함수에 인자값으로 True를 넣어서 dl/{setID} 가 삭제 되지 않으므로 여기서 폴더 삭제함
        shutil.rmtree(f"data/dl/{setID}")