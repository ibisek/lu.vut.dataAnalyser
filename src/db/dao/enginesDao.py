from typing import List

from db.dao.alchemy import Alchemy
from utils.singleton import Singleton
from configuration import dbConnectionInfo
from db.DbSource import DbSource


class EnginesDao(Alchemy, Singleton):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.engines

    @staticmethod
    def getEngineIdsForRawFlight(flightId: int) -> List[int]:
        ids = []

        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"select engine_id from engines_flights as ef " \
                     f"join flights as f on ef.flight_id = f.id " \
                     f"where f.id={flightId} and f.idx=0;"

            c.execute(strSql)

            rows = c.fetchall()
            for row in rows:
                ids.append(row[0])

        return ids

    @staticmethod
    def getProperty(engine, key):
        """
        :param engine:
        :param key:
        :return: (value, unit)
        """
        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"select v, unit from equipment_properties " \
                     f"where equipment_id = {engine.equipment_id} and k='{key}';"
            c.execute(strSql)

            row = c.fetchone()
            if row:
                return row[0], row[1]

        return None, None


if __name__ == '__main__':
    ud = EnginesDao()

    engine = ud.getOne(id=1)
    print(engine)

    engineIds = ud.getEngineIdsForRawFlight(flightId=1)
    print(engineIds)
