"""
Stores and retrieves flight recording data (time-series) to/from the INFLUX db.

https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_tutorial/
"""

from enum import Enum

from influxdb import DataFrameClient
from pandas.core.frame import DataFrame

from configuration import INFLUX_DB_HOST, INFLUX_DB_NAME
from db.InfluxDbThread import InfluxDbThread


class RecordingType(Enum):
    RAW = 'raw'
    FILTERED = 'fil'
    STANDARDIZED = 'std'


class FlightRecordingDao(object):

    def __init__(self):
        self.influx = InfluxDbThread(dbName=INFLUX_DB_NAME, host=INFLUX_DB_HOST)
        self.influx.start()

    def queueEmpty(self) -> bool:
        return self.influx.toDoStatements.empty()

    def storeDf(self, engineId: int, flightId: int, flightIdx: int, cycleId: int, cycleIdx: int, df: DataFrame, recType: RecordingType):
        keys = df.keys().tolist()
        if 'ts' in keys:
            keys.remove('ts')
        keys = sorted(keys)

        for row in df.iterrows():
            ts = int(row[0].timestamp() * 1000)

            rowSeries = row[1]
            kv = ",".join([f"{k}={rowSeries[k]}" for k in keys])

            s = f"flights,type={recType.value},flightId={flightId},flightIdx={flightIdx},engineId={engineId},cycleId={cycleId},cycleIdx={cycleIdx} {kv} {ts}000000"

            self.influx.addStatement(s)

    def __del__(self):
        self.influx.stop()

    @staticmethod
    def loadDf(engineId: int, flightId: int, flightIdx: int, cycleId: int, cycleIdx: int, recType: RecordingType=RecordingType.FILTERED) -> DataFrame:

        q = f"SELECT * FROM flights WHERE type='{recType.value}' AND engineId= '{engineId}' " \
                f"AND flightId = '{flightId}' AND flightIdx = '{flightIdx}' " \
                f"AND cycleId = '{cycleId}' AND cycleIdx = '{cycleIdx}'"

        c = DataFrameClient(host=INFLUX_DB_HOST, port=8086, database=INFLUX_DB_NAME)
        res = c.query(query=q)

        if len(res) == 0:
            print(f'[WARN] loadDf(): no data in result set for {recType.value} engine: {engineId}; flight: {flightId}; cycle: {cycleId}')
            return DataFrame()

        df = res['flights']

        # drop columns that are tags; we want to proceed with fields only:
        df = df.drop(columns=['cycleId', 'engineId', 'flightId', 'type'])
        if 'flightIdx' in df.keys():
            df.drop(columns=['flightIdx'])
        if 'cycleIdx' in df.keys():
            df.drop(columns=['cycleIdx'])

        # re-create the 'ts' channel/column:
        df['ts'] = df.index
        df['ts'] = df['ts'].apply(lambda x: x.timestamp())

        return df


if __name__ == '__main__':
    engineId = 1
    flightId = 1
    cycleId = 1

    df = FlightRecordingDao.loadDf(engineId=engineId, flightId=flightId, cycleId=cycleId, recType=RecordingType.FILTERED)

    print('HEAD:\n', df.head())

    print('KOHEU.')
