import numpy

from utils.singleton import Singleton

from db.dao.alchemy import Alchemy
from db.dao.cyclesFlightsDao import CyclesFlightsDao
from configuration import dbConnectionInfo
from db.DbSource import DbSource


class CyclesDao(Alchemy, Singleton):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.cycles

    @staticmethod
    def prepareForSave(cycle):
        """
        Converts numpy.float64 values into floats.
        The database does not understand such values.
        :param cycle:
        :return: nix
        """
        for attr in cycle.__dict__:
            val = getattr(cycle, attr)

            if type(val) == numpy.float64:
                setattr(cycle, attr, float(val))

    def delete(self, cycle):
        CyclesFlightsDao.delete(cycleId=cycle.id, flightId=None)
        super().delete(cycle)

    def listCyclesFor(self, engineId: int, flightId: int, flightIdx: int = None, cycleIdx: int = None) -> []:
        sql = f"SELECT c.id FROM cycles AS c " \
              f"JOIN cycles_flights as cf on cf.cycle_id = c.id " \
              f"JOIN flights as f on f.id = cf.flight_id " \
              f"WHERE f.id={flightId} AND c.engine_id={engineId}"
        if flightIdx is not None:
            sql += f" AND f.idx={flightIdx}"
        if cycleIdx is not None:
            sql += f" AND c.idx={cycleIdx}"
        sql += ';'

        cycleIds = []

        with DbSource(dbConnectionInfo).getConnection() as c:
            c.execute(sql)
            rows = c.fetchall()
            for row in rows:
                cycleIds.append(row[0])

        cycles = []
        for id in cycleIds:
            cycle = self.getOne(id=id)
            if cycle:
                cycles.append(cycle)

        return cycles


if __name__ == '__main__':
    dao = CyclesDao()
    cycle = dao.getOne(id=949)
    # print("1:", vars(cycle))

    cycle = dao.listCyclesFor(engineId=3, flightId=1696, flightIdx=0, cycleIdx=0)
    # print("2:", vars(cycle))

    print(666)
