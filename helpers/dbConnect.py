import json
import pymysql
from helpers import config
import traceback

from lets_common_log import logUtils as log

class db:
    def __init__(self, DBType, connectMsg=True):
        self.conf = config.config("config.ini")
        self.DB_HOST = self.conf.config["db"]["host"]
        self.DB_PORT = int(self.conf.config["db"]["port"])
        self.DB_USERNAME = self.conf.config["db"]["username"]
        self.DB_PASSWORD = self.conf.config["db"]["password"]
        self.DB_DATABASE = DBType
        self.connect(connectMsg)

    def connect(self, connectMsg=True):
        try:
            self.pydb = pymysql.connect(host=self.DB_HOST, port=self.DB_PORT, user=self.DB_USERNAME, passwd=self.DB_PASSWORD, db=self.DB_DATABASE, charset='utf8')
            self.cursor = self.pydb.cursor()
            if connectMsg: log.chat(f"{self.DB_DATABASE} DB로 연결됨")
        except Exception as e:
            log.error(f"{self.DB_DATABASE} DB 연결 실패! 에러: {e}")
            exit()

    def check_connection(self):
        try: self.cursor.execute("SELECT 1")
        except:
            log.error(traceback.format_exc())
            log.info("DB 연결이 끊어졌습니다. 재연결을 시도합니다.")
            self.close(); self.connect()

    def mogrify(self, sql, param=None): return self.cursor.mogrify(sql, param)

    def fetch(self, sql, param=None, NoneMsg=True):
        self.check_connection()
        if param is None or param == "": self.cursor.execute(sql)
        else: self.cursor.execute(sql, param)

        columns = [column[0] for column in self.cursor.description]
        result = self.cursor.fetchall()

        if not result:
            if NoneMsg: log.error(f"None | SQL = {self.cursor.mogrify(sql, param)}")
            return None
        elif len(result) == 1:
            data = {}
            for c, r in zip(columns, result[0]): data[c] = r
            return data
        else:
            d = []
            for i in result:
                data = {}
                for c, r in zip(columns, i): data[c] = r
                d.append(data)
            return d

    def execute(self, sql, param=None):
        self.check_connection()
        if param is None or param == "": self.cursor.execute(sql)
        else: self.cursor.execute(sql, param)
        return self

    def commit(self):
        self.check_connection()
        self.pydb.commit()

    def close(self, CloseMsg=True):
        if CloseMsg: log.info(f"{self.DB_DATABASE} db closed")
        self.pydb.close()