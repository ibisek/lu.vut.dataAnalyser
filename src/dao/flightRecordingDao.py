

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

    def storeDf(self, engineId: int, flightId: int, cycleId: int, df: DataFrame, recType: RecordingType):
        keys = df.keys().tolist()
        keys.remove('ts')
        keys = sorted(keys)

        for row in df.iterrows():
            ts = int(row[0].timestamp()*1000)

            rowSeries = row[1]
            kv = ",".join([f"{k}={rowSeries[k]}" for k in keys])

            s = f"flights,type={recType.value},flight_id={flightId},engine_id={engineId},cycle_id={cycleId} {kv} {ts}000000"

            self.influx.addStatement(s)

    def __del__(self):
        self.influx.stop()

    @staticmethod
    def loadDf(engineId: int, flightId: int, cycleId: int, recType: RecordingType) -> DataFrame:

        q = f"SELECT * FROM flights WHERE type='{recType.value}' AND engine_id='{engineId}' AND flight_id='{flightId}' AND cycle_id='{cycleId}'"

        c = DataFrameClient(host=INFLUX_DB_HOST, port=8086, database=INFLUX_DB_NAME)
        res = c.query(query=q)

        df = res['flights']

        # re-create the 'ts' channel/column:
        df['ts'] = df.index
        df['ts'] = df['ts'].apply(lambda x: x.timestamp())

        return df


if __name__ == '__main__':
    engineId = 0
    flightId = 0
    cycle_id = 0

    df = FlightRecordingDao.loadDf(engineId=engineId, flightId=flightId, cycleId=cycle_id, recType=RecordingType.FILTERED)

    print('HEAD:\n', df.head())

    print('KOHEU.')
