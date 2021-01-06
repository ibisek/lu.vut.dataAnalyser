from db.dao.alchemy import Alchemy

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base


class FilesFlightsDao(Alchemy):

    def __init__(self):
        super(FilesFlightsDao, self).__init__()
        self.table = self.base.classes.files_flights

        # declBase = declarative_base()
        # self.base = automap_base(declBase)
        # self.table = Table('files_flights', self.base.metadata,
        #                                    Column('file_id', Integer, ForeignKey('files.id')),
        #                                    Column('flight_id', Integer, ForeignKey('file.id')))


if __name__ == '__main__':
    ffDao = FilesFlightsDao()
    ff = ffDao.createNew()
    print(ff)
