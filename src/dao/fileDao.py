from enum import Enum
from collections import namedtuple

from configuration import dbConnectionInfo
from db.DbSource import DbSource


class FileStatus(Enum):
    UNDEF = 0
    READY_TO_PROCESS = 1
    UNDER_ANALYSIS = 2
    ANALYSIS_COMPLETE = 3
    FAILED = 255


class File(object):

    def __init__(self, id, name, flightId=None, engineId=None,
                 source=False, generated=False,
                 status=FileStatus.UNDEF, hash=None):
        self.id = id
        self.name = name
        self.flightId = flightId
        self.engineId = engineId
        self.source = source
        self.generated = generated
        self.status = status
        self.hash = hash

    def __str__(self):
        return f"#File: id: {self.id}\n name: {self.name}\n flightId: {self.flightId}\n engineId: {self.engineId}" \
               f"\n source: {self.source}\n generated: {self.generated}\n status: {self.status}" \
               f"\n hash: {self.hash}"


def getFileForProcessing():
    f = None

    with DbSource(dbConnectionInfo).getConnection() as c:
        strSql = f"SELECT * FROM files WHERE source = true AND status={FileStatus.READY_TO_PROCESS.value} LIMIT 1;"
        c.execute(strSql)

        rows = c.fetchall()
        for row in rows:
            (id, name, flightId, engineId, source, generated, status, hash) = row

            f = File(id=id, name=name, flightId=flightId, engineId=engineId,
                     source=source, generated=generated,
                     status=FileStatus(status), hash=hash)

    return f


def setFileStatus(file: File, status: FileStatus):
    with DbSource(dbConnectionInfo).getConnection() as c:
        strSql = f"UPDATE files SET status = {status.value} WHERE id = {file.id};"
        res = c.execute(strSql)
        if res:
            return True

    return False

