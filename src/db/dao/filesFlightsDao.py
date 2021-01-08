from db.dao.alchemy import Alchemy
from utils.singleton import Singleton
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base

from configuration import dbConnectionInfo
from db.DbSource import DbSource


class FileFlight:
    file_id = None
    flight_id = None

    def __init__(self, fileId=None, flightId=None):
        self.file_id = fileId
        self.flight_id = flightId


class FilesFlightsDao(Alchemy, Singleton):

    def __init__(self):
        super(FilesFlightsDao, self).__init__()
        # self.table = self.base.classes.files_flights

        # declBase = declarative_base()
        # self.base = automap_base(declBase)
        # self.table = Table('files_flights', self.base.metadata,
        #                                    Column('file_id', Integer, ForeignKey('files.id')),
        #                                    Column('flight_id', Integer, ForeignKey('file.id')))

    def createNew(self) -> FileFlight:
        return FileFlight()

    def save(self, ff: FileFlight):
        if not ff.file_id or not ff.flight_id:
            raise ValueError("Any of the IDs cannot be null!")
        if self.getOne(fileId=ff.file_id, flightId=ff.flight_id):
            return  # already there

        sql = f"INSERT INTO files_flights (file_id, flight_id) VALUES ({ff.file_id}, {ff.flight_id})"

        with DbSource(dbConnectionInfo).getConnection() as c:
            c.execute(sql)

    def getOne(self, fileId: int, flightId: int) -> FileFlight:
        if not fileId and not flightId:
            return None

        with DbSource(dbConnectionInfo).getConnection() as c:
            sql = f"SELECT file_id, flight_id FROM files_flights WHERE "
            if fileId:
                sql += f"file_id = {fileId} "
                if flightId:
                    sql += "AND "
            if flightId:
                sql += f"flight_id = {flightId}"

            c.execute(sql)

            row = c.fetchone()
            if row:
                (fiId, flId) = row
                return FileFlight(fiId, flId)

        return None


if __name__ == '__main__':
    ffDao = FilesFlightsDao()
    ff = ffDao.createNew()

    ff.file_id = 666
    ff.flight_id = 667

    ffDao.save(ff)
