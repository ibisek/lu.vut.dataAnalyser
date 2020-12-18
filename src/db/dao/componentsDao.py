from db.dao.alchemy import Alchemy

from configuration import dbConnectionInfo
from db.DbSource import DbSource


class ComponentsDao(Alchemy):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.components

    @staticmethod
    def _getProperty(component, key):
        with DbSource(dbConnectionInfo).getConnection() as c:
            strSql = f"select v, unit from equipment_properties " \
                     f"where equipment_id = {component.equipment_id} and k='{key}';"
            c.execute(strSql)

            row = c.fetchone()
            if row:
                return row[0], row[1]

        return None, None

    @staticmethod
    def getEqCyclesLimit(component):
        return ComponentsDao._getProperty(component, 'n')

    @staticmethod
    def getFlightCycleCoeffs(component):
        """
        :param component:
        :return: Av, Ap for given component
        """
        av, _ = ComponentsDao._getProperty(component, 'av')
        ap, _ = ComponentsDao._getProperty(component, 'ap')
        return av, ap

    @staticmethod
    def getFlightMissionCoeff(component):
        l, _ = ComponentsDao._getProperty(component, 'l')
        return l


if __name__ == '__main__':
    dao = ComponentsDao()
    c = dao.getOne(id=2)  # -> eq.id=8

    n, unit = dao.getEqCyclesLimit(c)
    print('n:', n, unit)

    av, ap = dao.getFlightCycleCoeffs(c)
    print(f'av: {av}\nap: {ap}')

    l = dao.getFlightMissionCoeff(c)
    print('l:', l)
