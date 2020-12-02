from typing import List

from db.dao.alchemy import Alchemy

from configuration import dbConnectionInfo
from db.DbSource import DbSource


class EnginesDao(Alchemy):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.engines

    @staticmethod
    def getEngineIdsForRawFlight(flightId: int) -> List[int]:
        ids = []

        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"select e.id from engines as e " \
                     f"join engines_flights as ef on e.id=ef.engine_id " \
                     f"join flights as f on ef.flight_id = f.id " \
                     f"where f.id={flightId} and f.idx=0;"
            c.execute(strSql)

            rows = c.fetchall()
            for row in rows:
                ids.append(row[0])

        return ids


if __name__ == '__main__':
    ud = EnginesDao()

    engine = ud.getOne(id=1)
    print(engine)

    engineIds = ud.getEngineIdsForRawFlight(flightId=1)
    print(engineIds)
