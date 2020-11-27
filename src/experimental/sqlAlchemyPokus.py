"""
https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91
https://docs.sqlalchemy.org/en/13/orm/tutorial.html
https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html
"""

import sqlalchemy as db

from configuration import SQLALCHEMY_DB_URI

if __name__ == '__main__':

    engine = db.create_engine(SQLALCHEMY_DB_URI, echo=True)
    # print(engine.table_names())

    conn = engine.connect()
    metadata = db.MetaData()
    flights = db.Table('flights', metadata, autoload=True, autoload_with=engine)

    # --

    query = db.select([flights])
    resultProxy = conn.execute(query)
    resultSet = resultProxy.fetchall()
    for res in resultSet:
        print("#Flight:")
        for key in res.keys():
            print('\t', key, ":", res[key])
        print()

    # --

    flightId = 1
    airplane_id = 3

    query = db.select([flights]).where(db.and_(flights.columns.id == flightId, flights.columns.airplane_id == airplane_id))
    resultProxy = conn.execute(query)
    resultSet = resultProxy.fetchall()
    for res in resultSet:
        print("#Flight:")
        for key in res.keys():
            print('\t', key, ":", res[key])
        print('')

    # --

    conn.close()
    print('KOHEU.')
