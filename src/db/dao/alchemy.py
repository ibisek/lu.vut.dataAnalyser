"""
Baseclass for DB via SqlAlchemy DAO access objects.
"""

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from configuration import SQLALCHEMY_DB_URI


class Alchemy(object):

    table = None    # placeholder for extending classes table object
    base = None
    session = None

    def __init__(self):
        if not self.base:
            self.base = automap_base()
            self.engine = create_engine(SQLALCHEMY_DB_URI)
            self.base.prepare(self.engine, reflect=True)

        if not self.session:
            self.session = Session(self.engine, autoflush=True)
            self.session.autoflush = True

    def __del__(self):
        # self.session.commit() # causes KeyError exception on a probably already-deleted object
        self.session.close()
        self.engine.dispose()

    def createNew(self):
        return self.table()

    def save(self, obj=None):
        if obj:
            try:
                self.session.add(obj)
            except Exception as e:
                pass

        self.session.commit()

        # if obj:
        #     objSession = None
        #     try:
        #         objSession = obj.object_session()
        #     except Exception:
        #         pass
        #
        #     try:
        #         if objSession:
        #             objSession.commit()
        #         else:
        #             self.session.add(obj)
        #             self.session.commit()
        #
        #     except Exception as e:
        #         # sqlalchemy.exc.InvalidRequestError: Object '<files at 0x7fd674f19550>' is already attached to session '1' (this is '7')
        #         # This makes a local copy while generated PK id WILL NOT be present in the original object!! :(
        #         local_object = self.session.merge(obj)
        #         self.session.add(local_object)
        #         self.session.commit()

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
        return q.first()
