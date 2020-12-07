import json
from db.dao.alchemy import Alchemy


class LogbookDao(Alchemy):

    def __init__(self):
        super(LogbookDao, self).__init__()
        self.table = self.base.classes.logbook


class Logbook:

    @staticmethod
    def add(ts: int, entry: str, engineId: int = None, airplaneId: int = None, componentId: int = None):
        if not engineId and not airplaneId and not componentId:
            raise ValueError('At least one of the IDs needs to be defined!')

        dao = LogbookDao()

        rec = dao.createNew()
        rec.ts = ts
        if engineId:
            rec.engine_id = engineId
        if airplaneId:
            rec.airplane_id = airplaneId
        if componentId:
            rec.component_id = componentId
        rec.entry = entry

        dao.save(rec)
