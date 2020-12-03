import json
from db.dao.alchemy import Alchemy


class LogbooksDao(Alchemy):

    def __init__(self):
        super(LogbooksDao, self).__init__()
        self.table = self.base.classes.logbooks


class Logbook:

    @staticmethod
    def add(ts: int, entry: dict, engineId: int = None, airplaneId: int = None, componentId: int = None):
        if not engineId and not airplaneId and not componentId:
            raise ValueError('At least one of the IDs must be defined!')

        dao = LogbooksDao()

        entry = dao.createNew()
        entry.ts = ts
        if engineId:
            entry.engine_id = engineId
        if airplaneId:
            entry.airplane_id = airplaneId
        if componentId:
            entry.component_id = componentId
        entry.entry = json.dumps(entry)

        dao.save(entry)
