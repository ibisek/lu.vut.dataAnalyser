from enum import Enum
from sqlalchemy.ext import automap

from db.dao.notificationsDao import NotificationsDao


class NotificationType(Enum):
    INFO = 1,
    VALUE_BELOW_LIMIT = 3,
    VALUE_ABOVE_LIMIT = 4,
    VALUE_OUT_OF_BOUNDS = 5,
    WARNING = 254,
    URGENT = 255


class Notifications:

    @staticmethod
    def _create(notifType: NotificationType, dbEntity: automap, message: str):

        notificationsDao = NotificationsDao()

        n = notificationsDao.createNew()
        n.type = notifType.value
        n.message = message
        n.checked = False

        if dbEntity.__class__.__name__ == 'airplanes':
            n.airplane_id = dbEntity.id
        elif dbEntity.__class__.__name__ == 'engines':
            n.engine_id = dbEntity.id
        elif dbEntity.__class__.__name__ == 'cycles':
            n.cycle_id = dbEntity.id
            n.engine_id = dbEntity.engine_id
            # n.flight_id = dbEntity.flight_id
        elif dbEntity.__class__.__name__ == 'flights':
            n.flight_id = dbEntity.id
        else:
            raise NotImplemented(type(dbEntity))

        notificationsDao.save(n)

    # convenience methods:

    @staticmethod
    def valOutOfBounds(dbEntity: automap, message: str):
        Notifications._create(NotificationType.VALUE_ABOVE_LIMIT, dbEntity, message)

    @staticmethod
    def valAboveLim(dbEntity: automap, message: str):
        Notifications._create(NotificationType.VALUE_ABOVE_LIMIT, dbEntity, message)

    @staticmethod
    def valBelowLim(dbEntity: automap, message: str):
        Notifications._create(NotificationType.VALUE_BELOW_LIMIT, dbEntity, message)

    @staticmethod
    def info(dbEntity: automap, message: str):
        Notifications._create(NotificationType.INFO, dbEntity, message)

    @staticmethod
    def warning(dbEntity: automap, message: str):
        Notifications._create(NotificationType.WARNING, dbEntity, message)

    @staticmethod
    def urgent(dbEntity: automap, message: str):
        Notifications._create(NotificationType.URGENT, dbEntity, message)
