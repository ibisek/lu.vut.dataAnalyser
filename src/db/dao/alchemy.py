"""
Baseclass for DB via SqlAlchemy DAO access objects.
"""

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from configuration import SQLALCHEMY_DB_URI


class Alchemy(object):

    table = None    # placeholder for extending classes table object

    def __init__(self):
        self.base = automap_base()
        engine = create_engine(SQLALCHEMY_DB_URI)
        self.base.prepare(engine, reflect=True)

        self.session = Session(engine)
        self.session.autoflush = True

    def __del__(self):
        # self.session.commit() # causes KeyError exception on a probably already-deleted object
        self.session.close()

    def createNew(self):
        return self.table()

    def save(self, obj=None):
        if obj:
            self.session.add(obj)

        self.session.commit()

    def get(self, **kwargs):
        """
        :param kwargs:
        :return: iterator on query results
        """
        q = self.session.query(self.table).filter_by(**kwargs)
        return iter(q)

    def getOne(self, **kwargs):
        """
        :param kwargs:
        :return: single instance of query result
        """
        q = self.session.query(self.table).filter_by(**kwargs).limit(1)
        return next(iter(q), None)
