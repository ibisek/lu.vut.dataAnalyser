"""
    Regression results with file_id == null are NOMINAL values (!)
"""

import numpy as np
import pandas as pd

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


def listFunctionsForEngine(engineId: int):
    """
    Lists all available regression functions for given engine.
    :param engineId:
    :return:
    """
    functions = list()

    sql = f"SELECT function FROM regression_results WHERE ts=0 AND file_id IS NULL AND engine_id={engineId};"

    dbs = DbSource(dbConnectionInfo=dbConnectionInfo)
    with dbs.getConnection() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            fn = row[0]
            functions.append(fn)

    return functions


def getValues(engineId: int, function: str):

    sql = f"SELECT ts, value FROM regression_results " \
          f"WHERE ts != 0 AND file_id IS NOT NULL AND " \
          f"engine_id = {engineId} AND function = '{function}' " \
          f"ORDER BY ts;"

    dbs = DbSource(dbConnectionInfo=dbConnectionInfo)
    with dbs.getConnection() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

        tss = np.zeros(len(rows))
        vals = np.zeros(len(rows))

        for i, row in enumerate(rows):
            tss[i] = row[0]
            vals[i] = row[1]

        df = pd.DataFrame(columns=['ts', 'value'])
        df['ts'] = tss
        df['value'] = vals

        # df.index = pd.to_datetime(df['ts'], unit='s')

    return df
