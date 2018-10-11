
import os
try:
    os.chdir('src')

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
from sqlalchemy.ext.declarative import declarative_base, as_declarative, declared_attr, DeferredReflection
from sqlalchemy.event import listens_for
from sqlalchemy.sql import select
from sqlalchemy.engine.reflection import Inspector


SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://DWENRG-SQL01\\DRIFTWOOD_DB/'
SQLALCHEMY_BINDS = {
    'iwell':        'iWell',
    'driftwood':      'Driftwood'
}

iwBase =  declarative_base()
# iwBase =  declarative_base(cls = DeferredReflection)
# iwBase = automap_base()

# TODO: Move to bottom
class iwell_agent(object):
    global iwBase
    __bind_key__ = 'iwell'
    engine = create_engine(SQLALCHEMY_DATABASE_URI+SQLALCHEMY_BINDS[__bind_key__])
    Session = sessionmaker(bind=engine)
    iwBase = declarative_base(bind=engine)

    # def __init__(self):
    #     iwBase.prepare(self.engine)







# Class to represent Database Table
# @as_declarative()
class WELLS(iwBase):

    # https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/table_config.html
    __bind_key__ = 'iwell'
    # __table__ = Table('WELLS', Base.metadata, autoload=True)
    
    __table_args__ = {'autoload': True}
    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    __tablename__ = 'WELLS'
    # @declared_attr
    # def __table__(cls):
    #     return Table(cls.__name__, iwBase.metadata, autoload=True)

    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__#.lower()

    # @classmethod
    # def __repr__(cls):
    #     return "<"+cls.__name__+"(\n %s)>" % ([x for x in cls.__table__.__dict__.values() 
    #                                     if x[0] in cls.__table__.primary_key.columns.keys()])

    @classmethod
    def get_pks(cls):
        # Return list of primary key column names
        return cls.__table__.primary_key.columns.keys()
    @classmethod
    def columns(cls):
        return cls.__table__.columns.keys()

    @classmethod
    def get_inspector(cls):
        return inspect(cls.__table__)

    @classmethod
    def get_existing(cls, session: Session, well_id: str = None):
        if well_id:
            return (session.query(cls.__table__))
        else:
            return session.query(cls.__table__).all()

    @classmethod
    def get_last_update(cls, session):
        return session.query(func.max(cls.__table__.c.updated)).first()

    @classmethod
    def nrows(cls):
        return cls.__table__.count().scalar()

    @classmethod
    def load_updates(cls, session: Session, updates: list) -> None:
            
        try:
            session.add_all(updates)
            # Commit Updates
            session.commit()
        except Exception as e:
            # TODO: Add Sentry
            session.rollback()
            session.close()
            print('Could not load updates')
            print(e)

    def load_inserts(cls, session: Session, inserts: pd.DataFrame) -> None:

        try:
            insert_records = []
            # To dict to pass to sqlalchemy
            for row in inserts.to_dict('records'):
                
                # Create record object and add to dml list
                insert_records.append(cls(**row))
            session.add_all(insert_records)

            # Commit Insertions
            session.commit()
        except Exception as e:
            # TODO: Add Sentry
            session.rollback()
            session.close()
            print('Could not load inserts')
            print(e)


agent = iwell_agent()
# agent = iwell_agent.engine

session = iwell_agent.Session()

# x = session.query(WELLS).all()

# session.rollback()

# WELLS.get_last_update()



#! --------------------------------------------------------------------------- !#

class WELL_NOTES(iwBase):

    __table__ = Table('WELL_NOTES', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('WELL_NOTES') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class WELL_GROUPS(iwBase):

    __table__ = Table('WELL_GROUPS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('WELL_GROUPS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class WELL_GROUP_WELLS(iwBase):

    __table__ = Table('WELL_GROUP_WELLS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('WELL_GROUP_WELLS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class TANKS(iwBase):

    __table__ = Table('TANKS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('TANKS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class TANK_READINGS(iwBase):

    __table__ = Table('TANK_READINGS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('TANK_READINGS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class RUN_TICKETS(iwBase):

    __table__ = Table('RUN_TICKETS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('RUN_TICKETS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class PRODUCTION_DAILY(iwBase):

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

class METERS(iwBase):

    __table__ = Table('METERS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('METERS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class METER_READINGS(iwBase):

    __table__ = Table('METER_READINGS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('METER_READINGS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class FIELDS_BY_WELL(iwBase):

    __table__ = Table('FIELDS_BY_WELL', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('FIELDS_BY_WELL') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class FIELDS(iwBase):

    __table__ = Table('FIELDS', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('FIELDS') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

class FIELD_VALUES(iwBase):

    __table__ = Table('FIELD_VALUES', iwBase.metadata, autoload=True)

    __mapper_args__ = {
        'exclude_properties' : ['updated', 'inserted']
    }
    def __repr__(self):
        return "<{}(\n %s)>".format('FIELD_VALUES') % ([x for x in self.__dict__.values() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()




class DEO_Wells(iwBase):
    __table__ = Table(deo_well_table
                    , iwBase.metadata
                    , autoload=True
                    , )

    def __repr__(self):
        return "<DEO Well(\n %s)>" % ([x for x in self.__dict__.items() 
                                        if x[0] in self.__table__.primary_key.columns.keys()])

    def get_pks(self):

        # Return list of primary key column names
        return self.__table__.primary_key.columns.keys()

    def columns(self):
        return self.__table__.columns.keys()

def prep_flowback(self, prod_df: pd.DataFrame) -> pd.DataFrame:
    
    prod_df.Timestamp = pd.to_datetime(prod_df.Timestamp, format="%m/%d/%Y %H:%M:%S %p")
    prod_df.Timestamp = prod_df.Timestamp + timedelta(milliseconds=0)

    prod_aliases = {
            'Timestamp' : 'prod_datetime',
            'WHT' : 'wh_temp',
            'Csg Psig' : 'wh_casing_press',
            'Tbg Psig' : 'wh_tubing_press',
            'Choke /64"' : 'wh_choke',
            'Sand' : 'sand',
            'Static PSIG' : 'sep_static_press',
            'Differential' : 'sep_differential',
            'Sep Temp' : 'sep_temp',
            'MCF/D' : 'gas',
            'Gas Accum' : 'gas_accum',
            'Total Oil Bbls' : 'oil_total',
            'Total Water Bbls' : 'water_total',
            'Water Left To Recover' : 'water_left_to_recover',
            '% Recovered' : 'water_recovered_pct',
            'Injection Accum' : 'injection_total',
            'Injection MCF/D' : 'injection_rate',
            'Amps' : 'amps',
            'Hertz' : 'hertz'
            }

    prod_df.rename(columns={k: v for k, v in prod_aliases.items()
                                    if v not in prod_df}
                                    , inplace = True)

    prod_df.columns = [x.lower() for x in prod_df.columns]

    # Drop columns not in table
    valid = [x for x in prod_df.columns if x in self.Flowback.columns(self.Flowback)]
    dropped = [x for x in prod_df.columns if x not in valid]
    prod_df = prod_df[valid]

    # TODO: Log instead of print
    print(''.join(['\n Input Dropped: {}'.format(x) for x in dropped ]))

    # Replace NaNs
    prod_df = prod_df.where(prod_df.notnull(), None)
    # pks = agent.Flowback.get_pks(agent.Flowback)
    # Get Table Ptrimary Keys
    pks = self.Flowback.get_pks(self.Flowback)
    # print(pks)
    # Remove rows with missing primary keys
    prod_df = prod_df.dropna(subset=pks)

    return prod_df

def get_existing_flowback(self, session: Session, api14: str):

        return session.query(self.Flowback) \
                    .filter(self.Flowback.api14 == api14) \
                    .all()

def load_flowback_updates(self, session: Session, updates: list) -> None:
    
    try:
        session.add_all(updates)
        # Commit Updates
        session.commit()

    except Exception as e:
        # TODO: Add Sentry
        session.rollback()
        session.close()
        print('Could not load updates')
        print(e)

def load_flowback_inserts(self, session: Session, inserts: pd.DataFrame) -> None:

    try:
        
        insert_records = []
        # To dict to pass to sqlalchemy
        for row in inserts.to_dict('records'):
            
            # Create record object and add to dml list
            insert_records.append(self.Flowback(**row))
            
        session.add_all(insert_records)

        # Commit Insertions
        session.commit()

    except Exception as e:
        # TODO: Add Sentry
        session.rollback()
        session.close()
        print('Could not load inserts')
        print(e)


def get_wellinfo(self, session = None, table='DEO_WELL_HEADER'):
        if session is None:
            session = self.Session()    

        query = session.query(self.DEO_Wells.api14
                , self.DEO_Wells.wellname
                , self.DEO_Wells.flowback_id)

        return pd.read_sql(query.statement
                    , query.session.bind
                    , index_col= self.DEO_Wells.api14.name)
        

def flowback_to_db(self, jobs: dict) -> None:
    """This is the workhorse of the flowback database integration.
    
    Arguments:
        prod_df {pd.DataFrame} -- a dataframe of production measurements
    
    Returns:
        None -- [description]
    """

    wellinfo = self.get_wellinfo()
    session = self.Session()
    pks = self.Flowback.get_pks(self.Flowback)
    # print(pks)

    for job_id in jobs.keys():
        d = wellinfo[wellinfo.flowback_id == job_id] \
            .reset_index() \
            .squeeze() \
            .to_dict()

        # job['upd_df']
        
        job = jobs[job_id]
        prod_df = job['prod_df']
        
        job['api14'] = d['api14']
        job['wellname'] = d['wellname']

        # Add wellinfo to new production dataframe
        prod_df['api14'] = d['api14']
        prod_df['wellname'] = d['wellname']

        # Clean up data for move to database
        prod_df = self.prep_flowback(prod_df)

        # Retrieve flowback already existing in the database for the current api14
        eprod = self.get_existing_flowback(session, d['api14'])

        # List of existing production datetimes
        edt = [dt.prod_datetime for dt in eprod]

        # Bool mask: Does a prod record for this api and datetime exist in the database?
        emask = prod_df.prod_datetime.isin(edt)
        # print(emask)
        # pprint(prod_df.head())
        # Remove duplicates
        prod_df = prod_df \
                .sort_values(pks, axis = 0, ascending = False) \
                .drop_duplicates(keep ='first', subset = pks)

        # Rows with a PK already in the database
        potential_updates = prod_df[emask] 

        # Rows that dont have an existing PK in the database
        inserts = prod_df[~emask]
        # print(inserts)
        updates = []
        for idx, row in potential_updates.iterrows():
            f = self.Flowback(**row.to_dict())
            if f in edt:
                updates.append(f)

        self.load_flowback_updates(Session(), updates)

        self.load_flowback_inserts(Session(), inserts)

        print('\n{} -- Inserted: {} | Updated: {}'.format(d['wellname'] or 'Missing', len(inserts) or 0, len(updates) or 0))

        # Close session
        session.close()


def poll_updated_production(self, thresh: datetime, api14 = None) -> pd.DataFrame:
    """ Check the database for new/updated production records"""

    session = self.Session()
    query = None

    if api14 is not None:
        # Query by api
        query = session.query(self.Flowback.api14, self.Flowback.job_id
                            , func.count(self.Flowback.prod_datetime).label('record_count')) \
                    .filter((self.Flowback.api14 == api14) \
                    | (self.Flowback.prod_datetime >= thresh)) \
                    .group_by(self.Flowback.api14, self.Flowback.job_id)
    else:
        # Query all
        query = session.query(self.Flowback.api14, self.Flowback.job_id
                            , func.count(self.Flowback.prod_datetime).label('record_count')) \
                    .filter(self.Flowback.prod_datetime >= thresh) \
                    .group_by(self.Flowback.api14, self.Flowback.job_id)

    if query is not None:
        return pd.read_sql(query.statement
                    , query.session.bind
                    , index_col = self.Flowback.api14.name)
    else:
        return pd.DataFrame()

def test() -> None:

        agent = flowback_agent()

        # create session
        Session = sessionmaker(bind=agent.engine)
        session = Session()
        prod_df = pd.read_excel('test\\data\\report#134-2018-09-18.xlsx'
                                , skiprows = 4
                                , header=[1]
                                , parse_dates = ['Timestamp'])

        # Enrich
        api10 = '0000000000'
        # prod_df['API10'] = api10
        prod_df['Job_ID'] = '134'

        # Clean up data for move to database
        prod_df = agent.prep_flowback(prod_df)

        # Get flowback already in database
        existing = agent.get_existing_flowback(session)

        # Check which records already exist in table
        prod_df = pd.merge(prod_df
                        , existing
                        , on= ['API10', 'Prod_Datetime']
                        , indicator = True
                        , how = 'outer')

        # prod_df.dtypes


        # Select only records that DO NOT exist in database and drop _merge column
        inserts = prod_df.query('_merge=="left_only"').drop('_merge', axis = 1)

        # Select only records that exist in database and drop _merge column
        updates = prod_df.query('_merge=="both"').drop('_merge', axis = 1)


        agent.load_flowback_updates(session, updates)


        agent.load_flowback_inserts(session, inserts)

        print('\nRows Inserted: {} | Updated: {}'.format(len(inserts), len(updates)))

        # Close session
        session.close()





if __name__ == '__main__':
    pass


agent = iwell_agent()

session = agent.Session()

agent.get_existing_wells()

agent._wells.retrieve(WELLS, session = session, well_id = 17417)


agent.__dir__()

wells.columns()

wells.get_existing_flowback(session = session, well_id = '17417')

session.query(agent._wells.__table__).filter('well_id = 17417').all()

wells.get_pks()


agent._wells.well_id = 17417

session.query(wells.__table__).all()

i = wells.get_inspector()

i.select().execute().fetchall()

i.count().__dir__()

i.count().c

select(i.count())

dir(session.query())

session.connection().engine

__table__

"<WELLS(\n %s)>" % ([x for x in wells.__dict__.values() 
                                    if x in wells.__table__.primary_key.columns.keys()])


def __repr__(self):
    return "<WELLS(\n %s)>" % ([x for x in self.__dict__.values() 
                                    if x[0] in self.__table__.primary_key.columns.keys()])

def get_pks(self):

    # Return list of primary key column names
    return self.__table__.primary_key.columns.keys()

def columns(self):
    return self.__table__.columns.keys()

def get_inspector(self):
    return inspect(self.__table__)

def get_existing_flowback(self, session: Session, well_id: str):

        return (session.query(self)
                    .filter(self.well_id == well_id)
                    .all())