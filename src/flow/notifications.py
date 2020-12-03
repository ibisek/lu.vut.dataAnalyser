from enum import Enum
from sqlalchemy.ext import automap

from db.dao.notificationsDao import NotificationsDao


class NotificationType(Enum):
    INFO = 1,
    VALUE_BELOW_LIMIT = 3,
    VALUE_ABOVE_LIMIT = 4,
    WARNING = 254,
    URGENT = 255


class Notifications:

    @staticmethod
    def _create(type: NotificationType, cycle: automap, message: str):

        notificationsDao = NotificationsDao()

        n = notificationsDao.createNew()
        n.type = type.value
        n.engine_id = cycle.engine_id
        n.flight_id = cycle.flight_id
        n.cycle_id = cycle.id
        n.message = message
        n.checked = False

        notificationsDao.save(n)

    # convenience methods:

    @staticmethod
    def valAboveLim(cycle: automap, message: str):
        Notifications._create(NotificationType.VALUE_ABOVE_LIMIT, cycle, message)

    @staticmethod
    def valBelowLim(cycle: automap, message: str):
        Notifications._create(NotificationType.VALUE_BELOW_LIMIT, cycle, message)

    @staticmethod
    def info(cycle: automap, message: str):
        Notifications._create(NotificationType.INFO, cycle, message)

    @staticmethod
    def warning(cycle: automap, message: str):
        Notifications._create(NotificationType.WARNING, cycle, message)

    @staticmethod
    def urgent(cycle: automap, message: str):
        Notifications._create(NotificationType.URGENT, cycle, message)
