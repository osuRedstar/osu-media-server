import json
import pymysql
import config

from lets_common_log import logUtils as log

class db:
    def __init__(self, DBType):
        self.conf = config.config("config.ini")

        self.DB_HOST = self.conf.config["db"]["host"]
        self.DB_PORT = int(self.conf.config["db"]["port"])
        self.DB_USERNAME = self.conf.config["db"]["username"]
        self.DB_PASSWORD = self.conf.config["db"]["password"]
        self.DB_DATABASE = self.conf.config["db"]["database"]
        self.DB_DATABASE_CHEESEGULL = self.conf.config["db"]["database-cheesegull"]
        self.OSU_APIKEY = self.conf.config["osu"]["apikey"]

        if DBType.lower() == "redstar":
            self.DB_DATABASE_NOW = self.DB_DATABASE
        elif DBType.lower() == "cheesegull":
            self.DB_DATABASE_NOW = self.DB_DATABASE_CHEESEGULL
        else:
            self.DB_DATABASE_NOW = self.DB_DATABASE_CHEESEGULL
            log.debug(f"예외 | {DBType} DB로 연결함")

        try:
            self.pydb = pymysql.connect(host=self.DB_HOST, port=self.DB_PORT, user=self.DB_USERNAME, passwd=self.DB_PASSWORD, db=self.DB_DATABASE_NOW, charset='utf8')
        except:
            log.error(f"{self.DB_DATABASE_NOW} DB 연결 실패!")
            exit()

    def fetch(self, sql, param):
        cursor = self.pydb.cursor()
        if param is None or param == "":
            cursor.execute(sql)
        else:
            cursor.execute(sql, param)

        columns = [column[0] for column in cursor.description]
        result = cursor.fetchall()
        self.pydb.close()

        if not result:
            log.error(f"None | SQL = {cursor.mogrify(sql, param)}")
            return None
        elif len(result) == 1:
            data = {}
            for c, r in zip(columns, result[0]):
                data[c] = r
            return data
        else:
            d = []
            for i in result:
                data = {}
                for c, r in zip(columns, i):
                    data[c] = r
                d.append(data)
            return d
        
    def execute(self, sql, param):
        cursor = self.pydb.cursor()
        if param is None or param == "":
            cursor.execute(sql)
        else:
            cursor.execute(sql, param)
        self.pydb.commit()
        self.pydb.close()