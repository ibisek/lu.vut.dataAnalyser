"""
    Regression results with file_id == null are NOMINAL values (!)
"""

from db.DbSource import DbSource

from configuration import dbConnectionInfo
from dao.fileDao import File
from dataAnalysis.regression import RegressionResult


def saveRegressionResult(res: RegressionResult, file: File = None, engineId: int = None):
    """
    Specify either file or just engineId.
    :param res:
    :param file:
    :param engineId:
    :return:
    """

    delSql = None
    insertSql = None

    if file:
        delSql = f"DELETE FROM regression_results WHERE engine_id={file.engineId} AND file_id={file.id};"
        insertSql = f"INSERT INTO regression_results (ts, engine_id, file_id, function, value, a, b, c, x_min, x_max) " \
                    f"VALUES ({res.ts}, {file.engineId}, {file.id}, '{res.fn}', {res.val}, {res.a}, {res.b}, {res.c}, {res.xMin}, {res.xMax});"
    else:
        delSql = f"DELETE FROM regression_results WHERE engine_id={engineId} AND function='{res.fn}' AND file_id IS NULL;"
        insertSql = f"INSERT INTO regression_results (engine_id, function, value, a, b, c, x_min, x_max) " \
                    f"VALUES ({engineId}, '{res.fn}', {res.val}, {res.a}, {res.b}, {res.c}, {res.xMin}, {res.xMax});"

    dbs = DbSource(dbConnectionInfo=dbConnectionInfo)
    with dbs.getConnection() as cur:
        # delete previously calculated results for this file:
        if delSql:
            cur.execute(delSql)

        if insertSql:
            cur.execute(insertSql)
