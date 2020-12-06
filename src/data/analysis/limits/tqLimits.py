import numpy as np
from itertools import product
from enum import Enum
from PIL import Image


class Zone(Enum):
    A = [0, 255, 0]  # green
    B = [0, 0, 255]  # blue
    C = [255, 0, 0]  # red


class TqLimits:
    FILE_PATH = 'images/tqLimits.png'
    X_RANGE = (0, 300)  # [s]
    Y_RANGE = (100.1, 108)  # [%]

    def __init__(self):
        self._loadImage(self.FILE_PATH)

    def _loadImage(self, filePath):
        image = Image.open(filePath)
        # print('img format:', image.format)
        # print('img size:  ', image.size)
        # print('img mode:  ', image.mode)
        # image.show()

        self.imgArr = np.asarray(image)
        (rows, cols, depth) = self.imgArr.shape
        # indexing: [row, col]
        # [0,0] = left upper corner
        self.width = cols
        self.height = rows

    def getZone(self, xVal, yVal):
        xPx = round(time / self.X_RANGE[1] * self.width)
        yPx = round((tq - self.Y_RANGE[0]) / (self.Y_RANGE[1] - self.Y_RANGE[0]) * self.height)

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

        idx = TqLimits._getIndexOfVal(color, max(color))
        if idx == 0:    # red
            return Zone.C
        elif idx == 1:  # green
            return Zone.A
        elif idx == 2:  # blue
            return Zone.B
        else:
            raise ValueError(f'Can not determine zone for {color}')


if __name__ == '__main__':
    tql = TqLimits()

    time = 25  # [s]
    tq = 105  # [%]
    zone = tql.getZone(xVal=time, yVal=tq)
    print(time, tq, zone, zone == Zone.A)

    time = 13  # [s]    # na hrane
    tq = 107  # [%]
    zone = tql.getZone(xVal=time, yVal=tq)
    print(time, tq, zone, zone == Zone.C)

    time = 61  # [s]
    tq = 102  # [%]
    zone = tql.getZone(xVal=time, yVal=tq)
    print(time, tq, zone, zone == Zone.B)

    time = 250  # [s]
    tq = 101  # [%]
    zone = tql.getZone(xVal=time, yVal=tq)
    print(time, tq, zone, zone == Zone.B)

    time = 30  # [s]
    tq = 107  # [%]
    zone = tql.getZone(xVal=time, yVal=tq)
    print(time, tq, zone, zone == Zone.C)

    time = 120  # [s]
    tq = 106  # [%]
    zone = tql.getZone(xVal=time, yVal=tq)
    print(time, tq, zone, zone == Zone.C)
