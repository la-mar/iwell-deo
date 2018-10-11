


import os
try:
    os.chdir('production_crutch')

except:
    pass

finally:
    os.getcwd()

from pprint import pprint

import pandas as pd
import pymssql

from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.event import listens_for
from sqlalchemy.sql import select
from sqlalchemy.engine.reflection import Inspector


# SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://DWENRG-SQL01/DRIFTWOOD_DB'
# SQLALCHEMY_BINDS = {
#     'iwell':        'iWell',
#     'driftwood':      'Driftwood'
# }


iwBase =  declarative_base()


class iwell_agent(object):
    global iwBase

    s = 'DWENRG-SQL01\\DRIFTWOOD_DB'
    db = 'iWell'
    engine = create_engine('mssql+pymssql://{0}/{1}'.format(s, db))
    Session = sessionmaker(bind=engine)
    iwBase =  declarative_base(bind=engine)
    # _wells = WELLS()

    def get_existing_wells(self):
        self._wells.retrieve(self._wells, session = self.Session())








# Class to represent Database Table
class PROD(iwBase):

    __table__ = Table('PRODUCTION_DAILY', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated'
                              , 'inserted'
                              , 'prod_date'
                              , 'prod_year'
                              , 'prod_month'
                              , 'prod_day'
                              ]
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('PRODUCTION_DAILY') % ([x for x in self.__dict__.values()
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):
        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

    def get_inspector(self):
        return inspect(self.__table__)

    def get_existing(self, session: Session, well_id: str = None):
        if well_id:
            return (session.query(self.__table__))
        else:
            return session.query(self.__table__).all()

    def get_last_update(self, session):
        
        return session.query(func.max(agent._wells.__table__.c.updated)).first()

    def nrows(self):
        return self.__table__.count().scalar()

    






def main():
    pass

if __name__ == '__main__':
    main()

from hackrequest import *

agent = iwell_agent()

session = agent.Session()

# session.query(PROD.__table__).all()

existing = PROD().get_existing(session)






wells = iWell(url+wells_path, 'wells')

wells.request_entity()

well_ids = wells.df.id.tolist()




session.execute('''TRUNCATE TABLE PRODUCTION_DAILY''')
session.commit()

getProduction(well_ids)








