from db.dao.alchemy import Alchemy


class CyclesDao(Alchemy):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.cycles
