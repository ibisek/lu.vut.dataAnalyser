import numpy as np
from itertools import product
from enum import Enum
from PIL import Image


class Zone(Enum):
    A = [0, 255, 0]  # green
    B = [0, 0, 255]  # blue
    C = [255, 0, 0]  # red


class LimitsBase:
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
        (rows, cols, depth) = self.imgArr.shape
        # indexing: [row, col]
        # [0,0] = left upper corner
        self.width = cols
        self.height = rows

    def getZone(self, xVal, yVal):
        xPx = round(xVal / self.X_RANGE[1] * self.width)
        yPx = round((yVal - self.Y_RANGE[0]) / (self.Y_RANGE[1] - self.Y_RANGE[0]) * self.height)

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
        if idx == 0:    # red
            return Zone.C
        elif idx == 1:  # green
            return Zone.A
        elif idx == 2:  # blue
            return Zone.B
        else:
            raise ValueError(f'Can not determine zone for {color}')
