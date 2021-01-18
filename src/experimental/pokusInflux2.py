from pandas import DataFrame
from dao.flightRecordingDao import FlightRecordingDao
from influxdb import InfluxDBClient

if __name__ == '__main__':
    dao = FlightRecordingDao()
    # df: DataFrame = dao.loadDf(engineId=1, flightId=1520, flightIdx=0, cycleId=308, cycleIdx=0)
    df: DataFrame = dao.loadDf(engineId=2, flightId=1700, flightIdx=2, cycleId=1560, cycleIdx=2)
    print(df.head())

    # from configuration import INFLUX_DB_HOST, INFLUX_DB_NAME
    # client = InfluxDBClient(host=INFLUX_DB_HOST, database=INFLUX_DB_NAME)

    # query = 'select * from flights limit 1'
    # result = client.query(query)
    # print(result)

    # q = f"SELECT * FROM flights WHERE type = $type AND engineId = $engineId " \
    #     f"AND flightId = $flightId AND flightIdx = $flightIdx " \
    #     f"AND cycleId = $cycleId AND cycleIdx = $cycleIdx"
    #
    # query = 'select * from flights where cycleId=$cycleId AND type=$type LIMIT 1;'
    # params = {'type': 'fil',
    #            'engineId': '2',
    #            'flightId': '1696',
    #            'flightIdx': '0',
    #            'cycleId': '1535',
    #            'cycleIdx': '0' }

    # print("Querying data: " + query)
    # result = client.query(query, bind_params=params)
    # print(result)
