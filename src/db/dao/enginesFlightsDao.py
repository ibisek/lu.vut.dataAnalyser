from db.dao.alchemy import Alchemy
from utils.singleton import Singleton
from configuration import dbConnectionInfo
from db.DbSource import DbSource


class EngineFlight:
    engine_id = None
    flight_id = None

    def __init__(self, engineId=None, flightId=None):
        self.engine_id = engineId
        self.flight_id = flightId


class EnginesFlightsDao(Alchemy, Singleton):

    def __init__(self):
        super(EnginesFlightsDao, self).__init__()
        # self.table = self.base.classes.engines_flights

    def createNew(self) -> EngineFlight:
        return EngineFlight()

    def save(self, ef: EngineFlight):
        if not ef.engine_id or not ef.flight_id:
            raise ValueError("Any of the IDs cannot be null!")

        if self.getOne(engineId=ef.engine_id, flightId=ef.flight_id):
            return  # already there

        sql = f"INSERT INTO engines_flights (engine_id, flight_id) VALUES ({ef.engine_id}, {ef.flight_id})"

        with DbSource(dbConnectionInfo).getConnection() as c:
            c.execute(sql)

    def getOne(self, engineId: int, flightId: int) -> EngineFlight:
        if not engineId and not flightId:
            return None

        with DbSource(dbConnectionInfo).getConnection() as c:
            sql = f"SELECT engine_id, flight_id FROM engines_flights WHERE "
            if engineId:
                sql += f"engine_id = {engineId} "
                if flightId:
                    sql += "AND "
            if flightId:
                sql += f"flight_id = {flightId}"

            c.execute(sql)

            row = c.fetchone()
            if row:
                (enId, flId) = row
                return EngineFlight(enId, flId)

        return None


if __name__ == '__main__':
    efDao = EnginesFlightsDao()
    ef = efDao.createNew()

    ef.engine_id = 666
    ef.flight_id = 667

    efDao.save(ef)
