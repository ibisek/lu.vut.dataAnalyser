

from enum import Enum

from pandas.core.frame import DataFrame
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

from configuration import INFLUX_DB_HOST, INFLUX_DB_NAME
from db.InfluxDbThread import InfluxDbThread


class RecordingType(Enum):
    RAW = 'raw'
    FILTERED = 'fil'
    STANDARDIZED = 'std'


class FlightRecordingDao(object):

    influx = InfluxDbThread(dbName=INFLUX_DB_NAME, host=INFLUX_DB_HOST)
    influx.start()

    def storeDfIntoInflux(self, engineId: int, flightId: int, cycleId: int, df: DataFrame, recType: RecordingType):
        keys = df.keys().tolist()
        keys.remove('ts')
        keys = sorted(keys)

        for row in df.iterrows():
            ts = int(row[0].timestamp())

            rowSeries = row[1]
            kv = ",".join([f"{k}={rowSeries[k]}" for k in keys])

            s = f"flights,type={recType.value[0]},flight_id={flightId},engine_id={engineId},cycle_id={cycleId} {kv} {ts}000000"

            self.influx.addStatement(s)

    def __del__(self):
        self.influx.stop()


