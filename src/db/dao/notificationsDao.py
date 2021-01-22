from db.dao.alchemy import Alchemy
from utils.singleton import Singleton


class NotificationsDao(Alchemy, Singleton):

    def __init__(self):
        super(NotificationsDao, self).__init__()
        self.table = self.base.classes.notifications

    def listMostRecent(self, limit=10):
        query = self.session.query(self.table).order_by(self.table.id.desc()).limit(limit)

        return query.all()


if __name__ == '__main__':
    notificationsDao = NotificationsDao()

    n = notificationsDao.createNew()

    notifications = notificationsDao.listMostRecent()
    for n in notifications:
        print("n:", n)

