import tornado.ioloop
import tornado.web
from helpers import logUtils as log
from functions import *
import json
import traceback
from helpers import requestsManager

class handler(requestsManager.asyncRequestHandler):
    def asyncGet(self):
        log.info("AAAAAAAAAAA")
        rm = request_msg(self, botpass=False)
        if rm != 200: return send403(self, rm)
        try:
            folder_path = f"{dataFolder}\\dl" #여기에 폴더 경로 설정
            ts = get_dir_size(folder_path)
            if not os.path.exists(folder_path): self.set_status(404); return self.write("Folder not found")
            self.set_header('Content-Type', 'application/zip')
            self.set_header('Content-Disposition', f'inline; filename="oszFiles_{ts}.zip"')
            self.set_header('Transfer-Encoding', 'chunked')

            """ #ZIP 파일을 실시간으로 생성하면서 스트리밍
            with zipfile.ZipFile(self, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_path):
                    log.debug(f"{root} | {_} | {files[:5]}")
                    for file in files:
                        if file.endswith(".osz"):
                            file_path = os.path.join(root, file); arcname = os.path.relpath(file_path, folder_path)
                            zipf.write(file_path, arcname)
                            if self.request.connection.stream.closed(): return #클라이언트가 연결을 끊었는지 확인 """

            file_list = [f for f in os.listdir(folder_path) if f.endswith('.osz')]
            # zipfile을 스트리밍 모드로 열기
            with zipfile.ZipFile(self, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
                for file_name in file_list:
                    print(" " * 180, end="\r"); print(f"{file_name}", end="\r")
                    file_path = os.path.join(folder_path, file_name)
                    # 파일이 존재하는지 확인
                    if not os.path.exists(file_path):
                        self.write(f"File not found: {file_name}\n")
                        continue  # 파일이 없으면 건너뛰기
                    if self.request.connection.stream.closed():
                        break  # 연결이 끊기면 전송 중지
                    # 파일을 압축해서 전송
                    try:
                        zip_file.write(file_path, os.path.basename(file_path))
                        self.flush()  # 클라이언트로 데이터 전송
                        tornado.ioloop.IOLoop.current().add_callback(self.flush)
                    except Exception as e:
                        self.write(f"Error compressing file {file_name}: {e}\n")
                        continue  # 오류 발생 시 건너뛰기
            
            # 만약 연결이 끊어지지 않으면 압축 전송 완료
            self.finish()
            
            """ import io
            buffer = io.BytesIO() #메모리 내에서 zip을 만들기 위한 버퍼 준비
            # ZIP 파일을 버퍼로 실시간으로 생성
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_path):
                    log.debug(f"{root} | {_} | {files[:5]}")
                    for file in files:
                        print(" " * 180, end="\r"); print(f"{file}", end="\r")
                        if file.endswith(".osz"):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, folder_path)
                            zipf.write(file_path, arcname)
            #버퍼의 내용을 클라이언트로 전송
            buffer.seek(0) #버퍼의 시작으로 이동
            self.write(buffer.read()) #버퍼 내용을 전송
            self.flush()
            if self.request.connection.stream.closed(): return log.warning("연결 끊음") #클라이언트 연결이 끊겼는지 확인 """

        except Exception as e:
            log.warning(e)
            log.error(f"\n{traceback.format_exc()}")
            return send503(self, e, "bsid", id)
        finally: self.set_header("Ping", str(resPingMs(self)))