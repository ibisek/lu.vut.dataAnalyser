from db.dao.alchemy import Alchemy


class NotificationsDao(Alchemy):

    def __init__(self):
        super(NotificationsDao, self).__init__()
        self.table = self.base.classes.notifications


if __name__ == '__main__':
    notificationsDao = NotificationsDao()

    n = notificationsDao.createNew()

