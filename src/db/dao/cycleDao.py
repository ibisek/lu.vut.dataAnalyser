from db.dao.alchemy import Alchemy


class CycleDao(Alchemy):

    def __init__(self):
        super(CycleDao, self).__init__()
        self.table = self.base.classes.cycles
