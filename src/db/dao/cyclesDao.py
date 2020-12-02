
import numpy

from db.dao.alchemy import Alchemy


class CyclesDao(Alchemy):

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
