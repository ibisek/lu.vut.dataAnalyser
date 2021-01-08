from db.dao.alchemy import Alchemy
from utils.singleton import Singleton


class EquipmentDao(Alchemy, Singleton):

    def __init__(self):
        super().__init__()
        self.table = self.base.classes.equipment
