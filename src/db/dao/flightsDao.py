from db.dao.alchemy import Alchemy


class FlightsDao(Alchemy):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.flights
