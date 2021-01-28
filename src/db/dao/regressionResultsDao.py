
from datetime import datetime
from pandas import DataFrame, read_sql

from db.DbSource import DbSource
from configuration import dbConnectionInfo
from db.dao.alchemy import Alchemy
from utils.singleton import Singleton


class RegressionResultsDao(Alchemy, Singleton):

    def __init__(self):
        super(RegressionResultsDao, self).__init__()
        self.table = self.base.classes.regression_results

    @staticmethod
    def listFunctions(engineId: int) -> []:
        """
        :param engineId:
        :return: list of processed functional dependencies, eg. ['ITT-fn-NG']
        """
        functions = []
        with DbSource(dbConnectionInfo).getConnection() as c:
            sql = f"SELECT DISTINCT(function) FROM regression_results WHERE engine_id={engineId};"
            c.execute(sql)
            for row in c.fetchall():
                functions.append(row[0])

        return functions

    @staticmethod
    def loadRegressionResultsData(engineId: int, function: str) -> DataFrame:
        with DbSource(dbConnectionInfo).getConnection() as c:
            sql = f"SELECT * FROM regression_results " \
                  f"WHERE engine_id = {engineId} AND function = '{function}' " \
                  f"ORDER BY ts;"
            df = read_sql(sql, c.connection)

            # create index as datetime:
            df.index = df['ts'].apply(lambda x: datetime.utcfromtimestamp(x))

        return df


if __name__ == '__main__':
    regressionResultsDao = RegressionResultsDao()
    rr = regressionResultsDao.createNew()
