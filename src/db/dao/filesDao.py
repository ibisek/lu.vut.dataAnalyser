from enum import Enum
from sqlalchemy import and_

from db.dao.alchemy import Alchemy
from utils.singleton import Singleton
from configuration import dbConnectionInfo
from db.DbSource import DbSource
from data.structures import FileFormat


class FileStatus(Enum):
    UNDEF = 0
    READY_TO_PROCESS = 1
    UNDER_ANALYSIS = 2
    ANALYSIS_COMPLETE = 3
    # >=128 error states
    NO_STEADY_STATES = 200  # no steady states detected
    FAILED = 255

    def translate(self, escape_table) -> int:
        return self.value


class File:

    def __init__(self, id, name, raw=False, format=FileFormat.UNDEFINED, status=FileStatus.UNDEF, hash=None):
        self.id = id
        self.name = name  # original filename
        self.raw = raw  # 0/1
        self.format = format
        self.status = status
        self.hash = hash  # SHA-256

    def __str__(self):
        return f"#File: id: {self.id}\n name: {self.name}\n raw: {self.raw}\n format: {self.format}\n status: {self.status}\n hash: {self.hash}"


class FilesDao(Alchemy, Singleton):
    def __init__(self):
        super(FilesDao, self).__init__()
        self.table = self.base.classes.files

    def getFileForProcessing(self):
        """
        :return: instance of ONE file which is ready for processing (typically a freshly uploaded file)
        """
        # from sqlalchemy import sql
        # cond = and_(self.base.classes.files.status == FileStatus.READY_TO_PROCESS.value,
        #             self.base.classes.files.format != FileFormat.UNDEFINED,
        #             self.base.classes.files.format != FileFormat.UNKNOWN)
        # cond = (self.base.classes.files.status == FileStatus.READY_TO_PROCESS.value) \
        #        & (self.base.classes.files.format != FileFormat.UNDEFINED) \
        #        & (self.base.classes.files.format != FileFormat.UNKNOWN)
        # file = super.getOne(cond)

        q = self.session.query(self.table).filter(
            and_(self.base.classes.files.status == FileStatus.READY_TO_PROCESS.value,
                 # self.base.classes.files.format != FileFormat.UNDEFINED.value,
                 self.base.classes.files.format != FileFormat.UNKNOWN.value)).limit(1)
        file = q.first()

        if file:
            if file.status is not None:
                file.status = FileStatus(file.status)  # from int value to object type
            if file.format is not None:
                file.format = FileFormat(file.format)  # from int value to object type

        return file

    def save(self, file):
        if file:
            # tmpStatus = file.status
            # tmpFormat = file.format
            #
            # file.status = file.status.value     # from object type to int
            # file.format = file.format.value     # from object type to int
            super(FilesDao, self).save(file)

            # file.status = tmpStatus
            # file.format = tmpFormat

        else:
            super(FilesDao, self).save()

    @staticmethod
    def listFiles(engineId: int = None):
        raise NotImplementedError()

    #
    #     eidCond = f"WHERE engine_id = {engineId}"
    #
    #     files = list()
    #
    #     with DbSource(dbConnectionInfo).getConnection() as c:
    #         strSql = f"SELECT id, name, raw, format, status, hash FROM files " \
    #                  f"{eidCond} " \
    #                  f"ORDER BY id;"
    #         c.execute(strSql)
    #
    #         rows = c.fetchall()
    #         for row in rows:
    #             (id, name, raw, format, status, hash) = row
    #             f = File(id=id, name=name, raw=raw, format=FileFormat(format), status=FileStatus(status), hash=hash)
    #             files.append(f)
    #
    #     return files

    @staticmethod
    def listFilesForNominalCalculation(engineId, limit=20):
        """
        :param engineId:
        :param limit:
        :return: list of first <limit> files for nominal values calculation
        """
        files = list()

        with DbSource(dbConnectionInfo).getConnection() as c:
            sql = f"SELECT f.id, f.name, f.raw, f.format, f.status, f.hash FROM files AS f " \
                f"JOIN files_flights AS ff ON f.id = ff.file_id " \
                f"JOIN flights AS fl ON fl.id = ff.flight_id " \
                f"JOIN engines_flights AS ef ON ef.flight_id = fl.id " \
                f"WHERE ef.engine_id = {engineId} AND status < 128 " \
                f"ORDER BY id LIMIT {limit};"
            c.execute(sql)

            rows = c.fetchall()
            for row in rows:
                (id, name, flightId, raw, format, status, hash) = row
                f = File(id=id, name=name, raw=raw, format=FileFormat(format), status=FileStatus(status), hash=hash)
                files.append(f)

        return files

    @staticmethod
    def setFileStatus(file: File, status: FileStatus):
        if not file or not file.id or not status:
            return

        with DbSource(dbConnectionInfo).getConnection() as c:
            sql = f"UPDATE files SET status = {status.value} WHERE id = {file.id};"
            res = c.execute(sql)
            if res:
                return True

        return False

    @staticmethod
    def save(file: File):
        if not file.id:  # new record
            sql = f"INSERT INTO files (name, raw, format, status, hash) " \
                f"VALUES ('{file.name}', {file.raw}, {file.format.value}, {file.status.value}, '{file.hash}');"

            with DbSource(dbConnectionInfo).getConnection() as c:
                c.execute(sql)
                file.id = c.lastrowid

        else:  # update existing
            sql = f"UPDATE files SET name='{file.name}', raw={file.raw}, format={file.format.value}, " \
                f"status={file.status.value}, hash='{file.hash}' " \
                f"WHERE id={file.id}"

            with DbSource(dbConnectionInfo).getConnection() as c:
                c.execute(sql)

        return file


if __name__ == '__main__':
    filesDao = FilesDao()
    file = filesDao.getOne(status=FileStatus.READY_TO_PROCESS.value, format=1)
    if file:
        print('file:', vars(file))
