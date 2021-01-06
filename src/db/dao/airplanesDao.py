from db.dao.alchemy import Alchemy


class AirplanesDao(Alchemy):

    def __init__(self):
        super(AirplanesDao, self).__init__()
        self.table = self.base.classes.airplanes


if __name__ == '__main__':
    airplanesDao = AirplanesDao()
    airplane = airplanesDao.getOne(id=1)
    print(airplane)
