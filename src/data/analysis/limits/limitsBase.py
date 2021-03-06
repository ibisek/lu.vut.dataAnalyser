"""
Base class for all limit-checking classes based on image region recognition.
"""

import numpy as np
from enum import Enum
from PIL import Image
from abc import ABCMeta, abstractmethod


class Zone(Enum):
    NONE = None
    A = [0, 255, 0]  # green
    B = [0, 0, 255]  # blue
    C = [255, 0, 0]  # red
    D = 'D'

    def ge(self, otherZone) -> bool:
        """
        Compares THIS zone to another zone.
        :param otherZone:
        :return: True if THIS zone is grater or equal (B>=A, C>=B ..)
        """
        if self.name == 'A' and (not otherZone or otherZone.name == 'NONE' or otherZone.name == 'A'):
            return True
        if self.name == 'B' and (otherZone.name == 'A' or otherZone.name == 'B'):
            return True
        if self.name == 'C' and (otherZone.name == 'A' or otherZone.name == 'B' or otherZone.name == 'C' ):
            return True
        if self.name == 'D' and (otherZone.name == 'A' or otherZone.name == 'B' or otherZone.name == 'C' or otherZone.name == 'D'):
            return True

        return False


class LimitsBase(metaclass=ABCMeta):
    FILE_PATH = None
    X_RANGE = None
    Y_RANGE = None

    def __init__(self):
        self._loadImage(self.FILE_PATH)

    def _loadImage(self, filePath):
        image = Image.open(filePath)
        # print('img format:', image.format)
        # print('img size:  ', image.size)
        # print('img mode:  ', image.mode)
        # image.show()

        self.imgArr = np.asarray(image)
        (rows, cols, _) = self.imgArr.shape
        # indexing: [row, col]
        # [0,0] = left upper corner
        self.width = cols
        self.height = rows

    def getZone(self, xVal: float, yVal: float):
        """
        :param xVal:
        :param yVal:
        :return: zone code in which the x-y vals are located
        """
        if xVal < self.X_RANGE[0] or xVal > self.X_RANGE[1] or yVal < self.Y_RANGE[0] or yVal > self.Y_RANGE[1]:
            raise ValueError(f'At least one of the values is out of range: xVal: {xVal}, yVal:{yVal}')

        xPx = int(round(xVal / self.X_RANGE[1] * self.width))
        yPx = int(round((yVal - self.Y_RANGE[0]) / (self.Y_RANGE[1] - self.Y_RANGE[0]) * self.height))

        row = self.height - yPx
        col = xPx
        zone = self._detectZone(self.imgArr[row, col])

        return zone

    @staticmethod
    def _getIndexOfVal(arr, val):
        for i in range(len(arr)):
            if arr[i] == val:
                return i

        raise ValueError(f'arr: {arr}, val: {val}')

    @staticmethod
    def _detectZone(color: np.ndarray) -> Zone:
        color = color[:3]
        if (color == Zone.A.value).all():  # green
            return Zone.A
        elif (color == Zone.B.value).all():  # blue
            return Zone.B
        elif (color == Zone.C.value).all():  # red
            return Zone.C

        idx = LimitsBase._getIndexOfVal(color, max(color))
        if idx == 0:  # red
            return Zone.C
        elif idx == 1:  # green
            return Zone.A
        elif idx == 2:  # blue
            return Zone.B
        else:
            raise ValueError(f'Can not determine zone for {color}')

    @abstractmethod
    def check(self, time: int, torque: float) -> Zone:
        pass
