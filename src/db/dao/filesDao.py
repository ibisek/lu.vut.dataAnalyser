from enum import Enum

from db.dao.alchemy import Alchemy

from configuration import dbConnectionInfo
from db.DbSource import DbSource
from data.structures import FileFormat


class FileStatus(Enum):
    UNDEF = 0
    READY_TO_PROCESS = 1
    UNDER_ANALYSIS = 2
    ANALYSIS_COMPLETE = 3
    # >=128 error states
    NO_STEADY_STATES = 200    # no steady states detected
    FAILED = 255


class File:

    def __init__(self, id, name, raw=False, format=FileFormat.UNDEFINED, status=FileStatus.UNDEF, hash=None):
        self.id = id
        self.name = name                # original filename
        self.raw = raw            # 0/1
        self.format = format
        self.status = status
        self.hash = hash          # SHA-256

    def __str__(self):
        return f"#File: id: {self.id}\n name: {self.name}\n raw: {self.raw}\n format: {self.format}\n status: {self.status}\n hash: {self.hash}"


class FilesDao(Alchemy):
    def __init__(self):
        super(FilesDao, self).__init__()
        self.table = self.base.classes.files

    @staticmethod
    def getFileForProcessing():
        """
        :return: instance of ONE file which is ready for processing (typically a freshly uploaded file)
        """
        f = None

        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"SELECT id, name, raw, format, status, hash FROM files " \
                     f"WHERE raw = true AND status={FileStatus.READY_TO_PROCESS.value} " \
                     f"and format!={FileFormat.UNDEFINED.value} and format!={FileFormat.UNKNOWN.value} " \
                     f"LIMIT 1;"
            c.execute(strSql)

            rows = c.fetchall()
            for row in rows:
                (id, name, raw, format, status, hash) = row
                f = File(id=id, name=name, raw=raw, format=FileFormat(format), status=FileStatus(status), hash=hash)

        return f

    @staticmethod
    def setFileStatus(file: File, status: FileStatus):
        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"UPDATE files SET status = {status.value} WHERE id = {file.id};"
            res = c.execute(strSql)
            if res:
                return True

        return False

    @staticmethod
    def listFiles(engineId: int = None):

        eidCond = f"WHERE engine_id = {engineId}"

        files = list()

        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"SELECT id, name, raw, format, status, hash FROM files " \
                     f"{eidCond} " \
                     f"ORDER BY id;"
            c.execute(strSql)

            rows = c.fetchall()
            for row in rows:
                (id, name, raw, format, status, hash) = row
                f = File(id=id, name=name, raw=raw, format=FileFormat(format), status=FileStatus(status), hash=hash)
                files.append(f)

        return files

    @staticmethod
    def listFilesForNominalCalculation(engineId, limit=20):
        """
        :param engineId:
        :param limit:
        :return: list of first <limit> files for nominal values calculation
        """
        files = list()

        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"SELECT id, name, raw, format, status, hash FROM files " \
                     f"WHERE engine_id = {engineId} AND status < 128 " \
                     f"ORDER BY id LIMIT {limit};"
            c.execute(strSql)

            rows = c.fetchall()
            for row in rows:
                (id, name, flightId, engineId, source, generated, status, hash) = row
                f = File(id=id, name=name, raw=raw, format=FileFormat(format), status=FileStatus(status), hash=hash)
                files.append(f)

        return files

    @staticmethod
    def save(file: File):
        flightId = 'null' if not file.flightId else file.flightId

        if not file.id:  # new record
            sql = f"INSERT INTO files (name, raw, format, status, hash) " \
                  f"VALUES ('{file.name}', {file.raw}, {file.format.value}, {file.status.value}, '{file.hash}');"

            with DbSource(dbConnectionInfo).getConnection() as c:
                c.execute(sql)
                file.id = c.lastrowid

        else:   # update existing
            sql = f"UPDATE files SET name='{file.name}', raw={file.raw}, format={file.format.value}, " \
                  f"status={file.status.value}, hash='{file.hash}' " \
                  f"WHERE id={file.id}"

            with DbSource(dbConnectionInfo).getConnection() as c:
                c.execute(sql)

        return file


if __name__ == '__main__':
    filesDao = FilesDao()
    file = filesDao.getOne(status=FileStatus.READY_TO_PROCESS.value, format=0)
    print('file:', vars(file))
