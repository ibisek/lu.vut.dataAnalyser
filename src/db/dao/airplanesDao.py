from db.dao.alchemy import Alchemy
from utils.singleton import Singleton


class AirplanesDao(Alchemy, Singleton):

    def __init__(self):
        super(AirplanesDao, self).__init__()
        self.table = self.base.classes.airplanes


if __name__ == '__main__':
    airplanesDao = AirplanesDao()
    airplane = airplanesDao.getOne(id=1)
    print(airplane)
