
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
from sqlalchemy.orm.util import object_state
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


_DEFAULT_EXCLUSIONS = ['updated', 'inserted']

iwBase =  declarative_base()
# iwBase =  declarative_base(cls = DeferredReflection)
# iwBase = automap_base()

# TODO: Move to bottom
class iwell_agent(object):
	# FIXME: Handle failed database connection
	global iwBase
	engine = create_engine(SQLALCHEMY_DATABASE_URI+SQLALCHEMY_BINDS['iwell'])
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
		
		df = df.dropna(subset = cls.get_pks())
		merged_objects = []
		for idx, row in df.iterrows():
			merged_objects.append(cls.session.merge(cls(**row.to_dict())))

		# Add merged objects to session
		cls.session.add_all(merged_objects)


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
			print('Could not load updates')
			print(e)

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
			print('Could not load inserts')
			print(e)

	@classmethod
	def persist(cls) -> None:
		"""Propagate changes in session to database. 
		
		Returns:
			None
		"""
		try:
			cls.session.commit()
			pprint(cls.get_session_state())
		except Exception as e:
			#TODO: Sentry
			print(e)
			cls.session.rollback()


class iWellTable(GenericTable):
	
	#** Default Metadata args for iWell tables
	__bind_key__ = 'iWell'
	__table_args__ = {'autoload': True}
	__mapper_args__ = {
					'exclude_properties' : _DEFAULT_EXCLUSIONS,
					}
	__tablename__ = None




# Class to represent Database Table
# @as_declarative()
class WELLS(iWellTable, iwBase):

	__tablename__ = 'WELLS'


class PROD(iWellTable, iwBase):

	__tablename__ = 'PRODUCTION_DAILY'
	__mapper_args__ = {
					'exclude_properties' : _DEFAULT_EXCLUSIONS + ['prod_date', 'prod_year', 'prod_month', 'prod_day'],
					}



