from db.dao.alchemy import Alchemy
from utils.singleton import Singleton


class NotificationsDao(Alchemy, Singleton):

    def __init__(self):
        super(NotificationsDao, self).__init__()
        self.table = self.base.classes.notifications


if __name__ == '__main__':
    notificationsDao = NotificationsDao()

    n = notificationsDao.createNew()

