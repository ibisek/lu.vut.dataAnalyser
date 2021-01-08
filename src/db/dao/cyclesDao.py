import numpy

from db.dao.alchemy import Alchemy
from utils.singleton import Singleton


class CyclesDao(Alchemy, Singleton):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.cycles

    @staticmethod
    def prepareForSave(cycle):
        """
        Converts numpy.float64 values into floats.
        The database does not understand such values.
        :param cycle:
        :return: nix
        """
        for attr in cycle.__dict__:
            val = getattr(cycle, attr)

            if type(val) == numpy.float64:
                setattr(cycle, attr, float(val))


if __name__ == '__main__':
    dao = CyclesDao()
    cycle = dao.getOne(id=949)
    print(vars(cycle))
