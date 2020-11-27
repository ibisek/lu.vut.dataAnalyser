"""
https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html
"""

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from configuration import SQLALCHEMY_DB_URI

base = automap_base()
engine = create_engine(SQLALCHEMY_DB_URI)
base.prepare(engine, reflect=True)

session = Session(engine)
session.autoflush = True

Users = base.classes.users
# u = Users(login='pepa', password='zkouska', salt='suul', name='Pepa', surname='z Depa', email='pepa@depo.cz', organisation_id=1)
# session.add(u)
# session.commit()

# --

# @see https://docs.sqlalchemy.org/en/13/core/selectable.html#sqlalchemy.sql.expression.select
# @see https://docs.sqlalchemy.org/en/13/orm/query.html
resList = session.query(Users).all()    # vraci cely object/row
resList = session.query(Users.login, Users.salt)    # vraci tuple
resList = session.query(Users).filter_by(login='ibisekx')  # vraci objekt / radek
for r in resList:
    print(r)
    print(r.__dict__)
    print(r.admin)
    r.salt = int(r.salt) + 1

session.commit()    # apply changes
# --


session.close()
print('KOHEU.')
