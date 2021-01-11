from db.dao.alchemy import Alchemy
from utils.singleton import Singleton


class RegressionResultsDao(Alchemy, Singleton):

    def __init__(self):
        super(RegressionResultsDao, self).__init__()
        self.table = self.base.classes.regression_results


if __name__ == '__main__':
    regressionResultsDao = RegressionResultsDao()
    rr = regressionResultsDao.createNew()
