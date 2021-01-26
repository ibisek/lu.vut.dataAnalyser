from db.dao.alchemy import Alchemy
from utils.singleton import Singleton
from db.DbSource import DbSource
from configuration import dbConnectionInfo


class NotificationsDao(Alchemy, Singleton):

    def __init__(self):
        super(NotificationsDao, self).__init__()
        self.table = self.base.classes.notifications

    def listMostRecent(self, limit=10):
        query = self.session.query(self.table).order_by(self.table.id.desc()).limit(limit)

        return query.all()

    @staticmethod
    def countNotificationsFor(airplaneId: int = None, engineId: int = None) -> {}:
        counts = {'sum': 0, 'info': 0, 'warning': 0, 'urgent': 0}
        if not airplaneId and not engineId:
            return counts

        with DbSource(dbConnectionInfo).getConnection() as c:
            if airplaneId is None:  # only engine & related cycles
                sql = f"SELECT COUNT(n.id), n.type from notifications AS n " \
                      f"JOIN cycles AS c ON c.id = n.cycle_id " \
                      f"WHERE n.engine_id={engineId} OR c.engine_id={engineId} " \
                      f"GROUP BY n.type;"

            else:   # airplane with engines & related cycles
                sql = f"SELECT COUNT(n.id), n.type from notifications AS n " \
                      f"JOIN cycles AS c ON c.id = n.cycle_id " \
                      f"WHERE n.airplane_id={airplaneId} " \
                      f"OR n.engine_id IN (SELECT id FROM engines WHERE airplane_id={airplaneId}) " \
                      f"OR c.engine_id IN (SELECT id FROM engines WHERE airplane_id={airplaneId}) " \
                      f"GROUP BY n.type;"

            c.execute(sql)

            counts = {'info': 0, 'warning': 0, 'urgent': 0}

            for row in c.fetchall():
                (count, notifType) = row

                if notifType <= 1:
                    counts['info'] += count
                elif notifType >= 255:
                    counts['urgent'] += count
                else:
                    counts['warning'] += count

        counts['sum'] = sum([v for k, v in counts.items()])

        return counts


if __name__ == '__main__':
    notificationsDao = NotificationsDao()

    n = notificationsDao.createNew()

    notifications = notificationsDao.listMostRecent()
    for n in notifications:
        print("n:", n)

