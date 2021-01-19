from db.dao.alchemy import Alchemy
from utils.singleton import Singleton
from configuration import dbConnectionInfo
from db.DbSource import DbSource


class CycleFlight:
    cycle_id = None
    flight_id = None

    def __init__(self, cycleId=None, flightId=None):
        self.cycle_id = cycleId
        self.flight_id = flightId


class CyclesFlightsDao(Singleton):

    def __init__(self):
        super(CyclesFlightsDao, self).__init__()

    @staticmethod
    def createNew() -> CycleFlight:
        return CycleFlight()

    def save(self, cf: CycleFlight):
        if not cf.cycle_id or not cf.flight_id:
            raise ValueError("Any of the IDs cannot be null!")

        if self.getOne(engineId=cf.cycle_id, flightId=cf.flight_id):
            return  # already there

        sql = f"INSERT INTO cycles_flights (cycle_id, flight_id) VALUES ({cf.cycle_id}, {cf.flight_id})"

        with DbSource(dbConnectionInfo).getConnection() as c:
            c.execute(sql)

    def getOne(self, engineId: int, flightId: int) -> CycleFlight:
        if not engineId and not flightId:
            return None

        with DbSource(dbConnectionInfo).getConnection() as c:
            sql = f"SELECT cycle_id, flight_id FROM cycles_flights WHERE "
            if engineId:
                sql += f"cycle_id = {engineId} "
                if flightId:
                    sql += "AND "
            if flightId:
                sql += f"flight_id = {flightId}"

            c.execute(sql)

            row = c.fetchone()
            if row:
                (cyId, flId) = row
                return CycleFlight(cyId, flId)

        return None

    @staticmethod
    def exists(cycleId: int, flightId: int):
        sql = f"SELECT count(*) FROM cycles_flights WHERE cycle_id={cycleId} AND flight_id={flightId};"

        with DbSource(dbConnectionInfo).getConnection() as c:
            c.execute(sql)
            res = c.fetchone()
            if res:
                count = res[0]
                if count > 0:
                    return True

        return False

    @staticmethod
    def delete(cycleId: int = None, flightId: int = None):
        sql = f"DELETE FROM cycles_flights WHERE cycle_id={cycleId} AND flight_id={flightId};"
        if not cycleId:
            sql = f"DELETE FROM cycles_flights WHERE flight_id={flightId};"
        elif not flightId:
            sql = f"DELETE FROM cycles_flights WHERE cycle_id={cycleId};"
        else:
            raise ValueError("Both argments must not be empty!")

        with DbSource(dbConnectionInfo).getConnection() as c:
            c.execute(sql)

    @staticmethod
    def listFlightIdsFor(cycleId: int):
        flightIds = []

        sql = f"SELECT flight_id FROM cycles_flights where cycle_id={cycleId};"
        with DbSource(dbConnectionInfo).getConnection() as c:
            c.execute(sql)
            for res in c.fetchone():
                flightId = res[0]
                flightIds.add(flightId)

        return flightIds


if __name__ == '__main__':
    cfDao = CyclesFlightsDao()

    # cf = cfDao.createNew()
    # cf.cycle_id = 666
    # cf.flight_id = 667
    #
    # cfDao.save(cf)

    print(cfDao.exists(cycleId=666, flightId=667))

    # cfDao.delete(cycleId=666)

