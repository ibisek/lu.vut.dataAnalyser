from db.dao.alchemy import Alchemy


class EnginesFlightsDao(Alchemy):

    def __init__(self):
        super(EnginesFlightsDao, self).__init__()
        self.table = self.base.classes.engines_flights
