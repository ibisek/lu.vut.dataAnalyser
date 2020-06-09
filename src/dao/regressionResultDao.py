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
        delSql = f"DELETE FROM regression_results WHERE engine_id={file.engineId} AND file_id={file.id} AND function = '{res.fn}';"
        insertSql = f"INSERT INTO regression_results (ts, engine_id, file_id, function, value, a, b, c, x_min, x_max) " \
                    f"VALUES ({res.ts}, {file.engineId}, {file.id}, '{res.fn}', {res.val}, {res.a}, {res.b}, {res.c}, {res.xMin}, {res.xMax});"
    else:
        delSql = f"DELETE FROM regression_results WHERE engine_id={engineId} AND function='{res.fn}' AND file_id IS NULL;"
        insertSql = f"INSERT INTO regression_results (engine_id, function, value, a, b, c, x_min, x_max) " \
                    f"VALUES ({engineId}, '{res.fn}', {res.val}, {res.a}, {res.b}, {res.c}, {res.xMin}, {res.xMax});"

    # print(f"[DEBUG] DEL: {delSql}")
    # print(f"[DEBUG] INS: {insertSql}")

    dbs = DbSource(dbConnectionInfo=dbConnectionInfo)
    with dbs.getConnection() as cur:
        # delete previously calculated results for this file:
        if delSql:
            cur.execute(delSql)

        if insertSql:
            cur.execute(insertSql)


def getRegressionResults(engineId: int, fileId: int):
    """
    Nominal regression results (per engine ID) are those with file_id set to null.
    :param engineId:
    :param fileId:
    :return: dict (for fileId=None) or list of all appropriate regression results
    """

    fileIdCond = f"= {fileId}" if fileId else "IS NULL"

    sql = f"SELECT id, ts, function, value, a, b, c, x_min, x_max FROM regression_results " \
          f"WHERE engine_id = {engineId} AND file_id {fileIdCond} " \
          f"ORDER BY file_id, function;"

    d = dict()
    l = list()

    dbs = DbSource(dbConnectionInfo=dbConnectionInfo)
    with dbs.getConnection() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            (id, ts, function, value, a, b, c, xMin, xMax) = row
            rr = RegressionResult(id=id, ts=ts, engineId=engineId, fileId=fileId, fn=function, val=value, a=a, b=b, c=c, xMin=xMin, xMax=xMax)

            if not fileId:
                d[function] = rr
            else:
                l.append(rr)

    if not fileId:
        return d
    else:
        return l

