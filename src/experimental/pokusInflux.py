"""
https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_tutorial
"""

import time

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

if __name__ == '__main__':

    DB_NAME = 'iot'

    client = InfluxDBClient(host='10.8.0.18', port=8086, database=DB_NAME)
    # client = InfluxDBClient(host='mydomain.com', port=8086, username='myuser', password='mypass', ssl=True, verify_ssl=True)

    ts = int(time.time())

    # id=4
    # fn='fn1\ aaa'
    # val=666
    # a=1
    # b=2
    # c=3
    # q = f"regression_results,id={id},fn={fn} val={val},a={a},b={b},c={c} {ts}000000000"

    dir = 140       # [deg]
    speed = 2.5     # [m/s]
    q = f"wind,loc=LKKA dir={dir},speed={speed} {ts}000000000"

    print(f"query: {q}")

    # data = [{"measurement": "regression_results",
    #          "tags": {
    #              "file_id": file.id,
    #              "engine_id": file.engineId,
    #              "fn": res.fn
    #          },
    #          "fields": {
    #              "val": res.val,
    #              "a": res.a,
    #              "b": res.b,
    #              "c": res.c,
    #          },
    #          "Timestamp": res.ts
    #          }]

    try:
        res = client.write(data=q, params={'db': DB_NAME}, expected_response_code=204, protocol='line')
        # client.write_points(data)

    except InfluxDBClientError as e:
        print(e)

    # --
    # client.query('SELECT "duration" FROM "pyexample"."autogen"."brushEvents" WHERE time > now() - 4d GROUP BY "user"')
    resultSet = client.query('SELECT * FROM wind')
    points = resultSet.get_points(tags={'loc': 'LKKA'})
    for p in points:
        print(p)

    # for res in resultSet:
    #     d = res[0]
    #     print(d)

    client.close()
