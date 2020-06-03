
from configuration import dbConnectionInfo
from db.DbSource import DbSource


def getConfiguration():
    configuration = dict()

    with DbSource(dbConnectionInfo).getConnection() as c:
        strSql = 'select * from configuration;'
        c.execute(strSql)

        rows = c.fetchall()
        for row in rows:
            (key, value) = row
            configuration[key] = value

    return configuration

