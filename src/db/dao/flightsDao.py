import numpy
from db.dao.alchemy import Alchemy
from utils.singleton import Singleton
from configuration import dbConnectionInfo
from db.DbSource import DbSource


class FlightsDao(Alchemy, Singleton):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.flights

    @staticmethod
    def getFlightIdForFile(fileId: int) -> int:
        flightId = None

        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"SELECT f.id FROM flights AS f " \
                     f"JOIN files_flights AS ff ON ff.flight_id = f.id " \
                     f"JOIN files AS fi ON fi.id = ff.file_id " \
                     f"WHERE fi.id={fileId};"
            c.execute(strSql)

            rows = c.fetchall()
            for row in rows:
                flightId = row[0]

        return flightId

    def save(self, flight):
        if not flight:
            super(FlightsDao, self).save()
        else:
            for k, v in flight.__dict__.items():
                if type(v) is numpy.float64:
                    setattr(flight, k, round(float(v), 6))  # all floats in flights database are (x,6)

            super(FlightsDao, self).save(flight)
