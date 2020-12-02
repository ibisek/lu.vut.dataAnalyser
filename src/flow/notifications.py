from enum import Enum

from db.dao.notificationsDao import NotificationsDao


class NotificationType(Enum):
    INFO = 1,
    WARNING = 2,
    VALUE_BELOW_LIMIT = 3,
    VALUE_ABOVE_LIMIT = 4


class Notifications:

    @staticmethod
    def _create(type: NotificationType, cycle, message: str):

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
    def createValAboveLim(cycle, message: str):
        Notifications._create(NotificationType.VALUE_ABOVE_LIMIT, cycle, message)

    @staticmethod
    def createValBelowLim(cycle, message: str):
        Notifications._create(NotificationType.VALUE_BELOW_LIMIT, cycle, message)

    @staticmethod
    def createInfo(cycle, message: str):
        Notifications._create(NotificationType.INFO, cycle, message)

    @staticmethod
    def createWarning(cycle, message: str):
        Notifications._create(NotificationType.WARNING, cycle, message)
