
import numpy as np
from pandas import DataFrame, Series


class IbiModel(object):
    def __init__(self, coefs: tuple = None):
        self.coefs = coefs

    def fit(self, x: Series, y: Series, deg: int):
        df = DataFrame()
        df['x'] = x
        df['y'] = y
        df.sort_values(by=['x'], inplace=True)

        self.coefs = np.polyfit(df['x'].values, df['y'].values, deg)  # a*x^2 + b*x + c

    def predictVal(self, x):
        y = 0
        for i, coef in enumerate(self.coefs):
            p = len(self.coefs) - i - 1
            y += pow(x, p) * coef if p > 0 else coef

        return y

    def predict(self, xSeries: Series):
        xValues = xSeries.values
        yValues = np.zeros(len(xValues))

        for ix, x in enumerate(xValues):
            y = 0

            for i, coef in enumerate(self.coefs):
                p = len(self.coefs) - i - 1
                y += pow(x, p) * coef if p > 0 else coef

            yValues[ix] = y

        return Series(yValues)


if __name__ == '__main__':
    # x = (1, 2, 3, 4, 6, 7, 8, 9, 5, 10)
    # y = (1, 4, 9, 16, 36, 49, 64, 81, 25, 100)
    x = (55000, 56000, 280000, 300000)
    y = (66, 66.5, 83, 84)

    df = DataFrame()
    df['x'] = np.asarray(x)
    df['y'] = np.asarray(y)

    m = IbiModel()
    m.fit(df['x'], df['y'], 2)
    print(m.coefs)

    y = m.predictVal(5)
    print(y)
    ys = m.predict(df['x'])
    print(ys)

