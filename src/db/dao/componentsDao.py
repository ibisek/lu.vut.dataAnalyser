from db.dao.alchemy import Alchemy

from configuration import dbConnectionInfo
from db.DbSource import DbSource


class ComponentsDao(Alchemy):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.components
