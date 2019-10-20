import logging
from datetime import datetime, timedelta
from pprint import pprint

import pandas as pd
from sqlalchemy import *
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import (DeferredReflection, as_declarative,
                                        declarative_base, declared_attr)
from sqlalchemy.orm import *
from sqlalchemy.orm.util import object_state
from sqlalchemy.sql import select

import pymssql
from settings import DATABASE_URI, DEFAULT_EXCLUSIONS, LOGLEVEL

logger = logging.getLogger(__name__)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

iwBase =  declarative_base()


class iwell_agent(object):

    global iwBase
    engine = create_engine(DATABASE_URI)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    iwBase = declarative_base(bind=engine)


class GenericTable(object):

    __bind_key__ = None
    # __table__ = Table('WELLS', Base.metadata, autoload=True)
    __table_args__ = None
    __mapper_args__ = None
    __tablename__ = None

    session = None


    @classmethod
    def get_pks(cls):
        # Return list of primary key column names
        return cls.__table__.primary_key.columns.keys()

    @classmethod
    def get_pk_cols(cls):
        pk_cols = []
        for k, v in cls.__table__.c.items():
            if v.primary_key:
                pk_cols.append(v)
        return pk_cols


    @classmethod
    def get_ids(cls):
        return cls.session.query(cls).with_entities(*cls.get_pk_cols()).all()

    @classmethod
    def keys(cls):
        query = cls.session.query(cls).with_entities(*cls.get_pk_cols())
        return list(pd.read_sql(query.statement, query.session.bind).squeeze().values)

    @classmethod
    def keyedkeys(cls):
        # return self.df[[self.aliases['id']]].to_dict('records')
        query = cls.session.query(cls).with_entities(*cls.get_pk_cols())
        return pd.read_sql(query.statement, query.session.bind).to_dict('records')

    @classmethod
    def cnames(cls):
        return cls.__table__.columns.keys()

    @classmethod
    def get_inspector(cls):
        return inspect(cls.__table__)

    @classmethod
    def get_existing_records(cls):
        return cls.session.query(cls).all()

    # FIXME:
    # @classmethod
    # def get_existing_ids(cls):
    #         return cls.session.query(cls.__table__.columns.keys()).all()
    @classmethod
    def get_session_state(cls, count = True) -> dict:
        if cls.session is not None:
            if count:
                return {'new' : len(cls.session.new),
                        'updates' : len(cls.session.dirty),
                        'deletes' : len(cls.session.deleted)
                        }
            else:
                return {'new' : cls.session.new,
                        'updates' : cls.session.dirty,
                        'deletes' : cls.session.deleted
                        }

    @classmethod
    def merge_records(cls, df: pd.DataFrame) -> None:
        """Convert dataframe rows to object instances and merge into session by
        primary key matching.

        Arguments:
            df {pd.DataFrame} -- A dataframe of object attributes

        Returns:
            None
        """
        if len(df) > 0:
            # Drop rows with NA in a primary key
            df = df.dropna(subset = cls.get_pks())

            merged_objects = []
            for idx, row in df.iterrows():
                merged_objects.append(cls.session.merge(cls(**row.to_dict())))

            # Add merged objects to session
            cls.session.add_all(merged_objects)
        else:
            logger.info('No records to update.')


    @classmethod
    def get_last_update(cls):
        return cls.session.query(func.max(cls.__table__.c.updated)).first()

    @classmethod
    def nrows(cls):
        return cls.session.query(func.count(cls.__table__.c.updated)).first()

    @classmethod
    def load_updates(cls, updates: list) -> None:
        try:
            cls.session.add_all(updates)
            # Commit Updates
            cls.session.commit()
        except Exception as e:
            # TODO: Add Sentry
            cls.session.rollback()
            # cls.session.close()
            logger.exception(f'Could not load updates -- {e}')

    @classmethod
    def load_inserts(cls, inserts: pd.DataFrame) -> None:

        try:
            insert_records = []
            # To dict to pass to sqlalchemy
            for row in inserts.to_dict('records'):

                # Create record object and add to dml list
                insert_records.append(cls(**row))
            cls.session.add_all(insert_records)

            # Commit Insertions
            cls.session.commit()
        except Exception as e:
            # TODO: Add Sentry
            cls.session.rollback()
            # cls.session.close()
            logger.exception(f'Could not load inserts -- {e}')

    @classmethod
    def persist(cls) -> None:
        """Propagate changes in session to database.

        Returns:
            None
        """
        try:
            cls.session.commit()
            logger.info(f'Persisted to {cls.__tablename__}')
        except Exception as e:
            logger.exception(f'Records not persisted. {e}')
            cls.session.rollback()


class iWellTable(GenericTable):

    #** Default Metadata args for iWell tables
    __bind_key__ = 'iWell'
    __table_args__ = {'autoload': True}
    __mapper_args__ = {
                    'exclude_properties' : DEFAULT_EXCLUSIONS,
                    }
    __tablename__ = None



# Class to represent Database Table
# @as_declarative()
class WELLS(iWellTable, iwBase):

    __tablename__ = 'WELLS'


class PROD(iWellTable, iwBase):

    __tablename__ = 'PRODUCTION_DAILY'
    __mapper_args__ = {
                    'exclude_properties' : DEFAULT_EXCLUSIONS + ['prod_date', 'prod_year', 'prod_month', 'prod_day'],
                    }


class METERS(iWellTable, iwBase):

    __tablename__ = 'METERS'


class METER_READINGS(iWellTable, iwBase):

    __tablename__ = 'METER_READINGS'


class FIELDS(iWellTable, iwBase):

    __tablename__ = 'FIELDS'


class FIELDS_BY_WELL(iWellTable, iwBase):

    __tablename__ = 'FIELDS_BY_WELL'

class FIELD_VALUES(iWellTable, iwBase):

    __tablename__ = 'FIELD_VALUES'


class TANKS(iWellTable, iwBase):

    __tablename__ = 'TANKS'


class TANK_READINGS(iWellTable, iwBase):

    __tablename__ = 'TANK_READINGS'


class WELL_TANKS(iWellTable, iwBase):

    __tablename__ = 'WELL_TANKS'


class RUN_TICKETS(iWellTable, iwBase):

    __tablename__ = 'RUN_TICKETS'


class WELL_NOTES(iWellTable, iwBase):

    __tablename__ = 'WELL_NOTES'

class WELL_GROUPS(iWellTable, iwBase):

    __tablename__ = 'WELL_GROUPS'


class WELL_GROUP_WELLS(iWellTable, iwBase):

    __tablename__ = 'WELL_GROUP_WELLS'
