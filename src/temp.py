
import os
os.getcwd()
os.chdir('src')
# os.getcwd()

import requests  # connect to apis
import json  # parse json if you need it
import pandas as pd  # dataframes
from pprint import pprint
from datetime import datetime, timedelta
# from retry import retry
from sqlalchemy import *
from sqlalchemy.orm import *


from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
from config import Config

client_id = "KTDMpqhGyBMhnRDB"
client_secret = "gYFRiXRtMN0fDYTDPUDYOk1RAbPz44Bu"
username = 'data@driftwoodenergy.com'
password = '7haYrAaFqTwS'

url = 'https://api.iwell.info/v1'
token_path = '/oauth2/access-token'
# request_path = '/me'
# wells_path = '/wells'


class iWell(object):
	# TODO: Add Requestor
	# TODO: Add database table
	
	cfg = Config('../config.yaml')
	s = 'DWENRG-SQL01\\DRIFTWOOD_DB'
	db = 'iWell'
	engine = create_engine('mssql+pymssql://{0}/{1}'.format(s, db))
	df = None
	
	def __init__(self, url, tbl):
		self.url = url
		self.tbl = tbl

	def _getAccessToken(self):
		"""Fetch a new access token from the provider."""
		# https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
		oauth = OAuth2Session(
			client=LegacyApplicationClient(client_id=client_id))
		return oauth.fetch_token(
			token_url=url+token_path, username=username, password=password, client_id=client_id, client_secret=client_secret
		)

	def _token_saver(self, response_token):
		"""Save response token and token expiration date to configuration file.
		Arguments:
			response_token {dict} -- oauth response object
		Returns:
			str -- response token as string
		"""

		self.cfg["token"] = response_token["access_token"]
		self.cfg["token_expiration"] = datetime.utcfromtimestamp(response_token['expires_at'])
		return response_token

	def getAccessToken(self):
		""" Checks if saved token is still valid"""
		token = self.cfg["token"]
		expiration = self.cfg["token_expiration"]

		# if expiration date exists and is a datetime
		if expiration is not None and isinstance(expiration, datetime):
			# if current time is < time of expiration minus one day
			if datetime.now() < expiration - timedelta(days=1):
				# print('Current token is valid.')
				return token

		# Token wasn't valid. Return new token
		print('Retrieved new token.')
		return self._token_saver(self._getAccessToken())

	def getBearer(self):
		"""Returns bearer authorization string for inclusion
			in request header.
		Returns:
			str -- bearer string
		"""

		return "Bearer " + self.getAccessToken()

	# @retry(tries = 3)
	def request_wells(self, all=True, apis=None):

		headers = {
			'Authorization': self.getBearer()
		}

		response = None

		try:
			response = requests.get(wells_url, headers=headers)
			return pd.read_json(response.text, orient='split')

		except Exception as e:
			# TODO: Sentry
			print(e)
			return None

	def clean_wells(self):
		"""Wrangling"""
		pass

	def getWells(self):
		""" Wrapper for request wells"""
		pass

	def temp_wells_to_db(self):
		# FIXME: Will be removed
		s = 'DWENRG-SQL01\\DRIFTWOOD_DB'
		db = 'iWell'
		engine = create_engine('mssql+pymssql://{0}/{1}'.format(s, db))
		wells.to_sql('WELL_HEADER', engine, if_exists='replace')

	def request_entity(self, orient='split', njson = False):

		headers = {
			'Authorization': self.getBearer()
		}

		response = None

		try:
			response = requests.get(self.url, headers=headers)
			if response.ok:
				if njson:
					self.df = pd.io.json.json_normalize(response.json()['data'])
				else:
					self.df = pd.read_json(response.text, orient=orient)
			else:
				print('     {path} - {message}'.format(
					path=response.request.path_url, message=response.json()['error']['message']))

		except Exception as e:
			#TODO: Sentry
			print(e)
			print('     Entity not retrieved.')
			self.df = None

	def entity_to_db(self):
		# FIXME: Will be removed
		if self.df is not None and not self.df.empty:
			self.df.to_sql(self.tbl, self.engine, if_exists='append', index=false)


if __name__ == '__main__':
	pass

# i = iWell()

# wells = i.request_wells()
# i.temp_wells_to_db()

# FIXME: FIX DATETIME OFFSETS

# FIXME: ENRICH WITH DEO DATA

# FIXME: ADD FOREIGN KEYS TO DATABASE

# FIXME: Normalize production across 24 hours


# FIXME:
# FIXME: ADD ?since flag to queries 
# FIXME:



def addsince(path, since = '1980-01-01'):
	return '?since={}'.format(int(pd.Timestamp(since).timestamp()))

url = 'https://api.iwell.info/v1'
token_path = '/oauth2/access-token'
request_path = '/me'

wells_path = '/wells'
wells_path = wells_path + addsince(wells_path)

well_tanks_path = '/well/{well_id}/tanks'
well_tanks_path = well_tanks_path + addsince(well_tanks_path)

tanks_path = '/tanks'
tanks_path = tanks_path + addsince(tanks_path)

readings_path = '/tanks/{tank_id}/readings'
readings_path = readings_path + addsince(readings_path)

reading_run_tickets_path = '/tanks/{tank_id}/readings/{reading_id}/run-tickets'
reading_run_tickets_path = reading_run_tickets_path + addsince(reading_run_tickets_path)

run_tickets_path = '/tanks/{tank_id}/readings/{reading_id}/run-tickets/{run_ticket_id}'

meters_path = '/wells/{well_id}/meters'
meters_path = meters_path + addsince(meters_path)

meter_readings_path = '/wells/{well_id}/meters/{meter_id}/readings'
meter_readings_path = meter_readings_path + addsince(meter_readings_path)

meter_readings_path = '/wells/{well_id}/meters/{meter_id}/readings'
meter_readings_path = meter_readings_path + addsince(meter_readings_path)

production_path = '/wells/{well_id}/production'
production_path = production_path + addsince(production_path)

well_groups_path = '/well-groups'
well_groups_path = well_groups_path + addsince(well_groups_path)

well_group_wells_path = '/well-groups/{group_id}/wells'
well_group_wells_path = well_group_wells_path + addsince(well_group_wells_path)

fields_path = '/fields'
fields_path = fields_path + addsince(fields_path)

well_fields_path = '/wells/{well_id}/fields'
well_fields_path = well_fields_path + addsince(well_fields_path)

well_field_values_path = '/wells/{well_id}/fields/{field_id}/values'
well_field_values_path = well_field_values_path + addsince(well_field_values_path)

validation_rules_path = '/wells/{well_id}/validation-rules'
validation_rules_path = validation_rules_path + addsince(validation_rules_path)

well_notes_path = '/wells/{well_id}/notes'
well_notes_path = well_notes_path + addsince(well_notes_path)











well_id_name = 'well_id'
tank_id_name = 'tank_id'
reading_id_name = 'reading_id'
run_ticket_id_name = 'run_ticket_id'
meter_id_name = 'meter_id'
well_groups_id_name = 'well_group_id'
field_id_name = 'field_id'
field_values_id_name = 'value_id'
production_id_name = 'production_id'
meter_reading_id_name = 'meter_reading_id'
validation_id_name = 'validation_id'
note_id_name = 'note_id'

#! -- WELLS --------------------------------------------------------------------

#! WELLS
df = pd.DataFrame()
p = wells_path
tbl = 'WELLS'
id_name = well_id_name

path = p
i = iWell(url=url+path, tbl=tbl)
i.request_entity()
i.df = i.df.rename(columns={'id': id_name
							,'name' : 'well_name'
							,'type' : 'well_type'
							,'updated_at' : 'updated_iwell'
							,'created_at' : 'created_iwell'
							,'alias' : 'well_alias'
							})
i.entity_to_db()
wells = i.df[id_name]
print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))

# #! WELL TANKS
# df = pd.DataFrame()
# p = well_tanks_path
# ids = wells
# tbl = 'WELL_TANKS'
# refid_name = 'well_id'

# for id in ids:
#     path = p.format(well_id = id)
#     i = iWell(url = url+path, tbl = tbl)
#     i.request_entity()
#     i.df[refid_name] = id
#     df = df.append(i.df, sort = True)
#     print('{path} - {count} records'.format(path = path, count = len(i.df)))

# i.df = df
# #? Add handing of Nonetype where DataFrame is expected
# i.entity_to_db()
# tank_readings = i.df[['id', refid_name]]
# print('{tbl} - {count} records loaded'.format(count = len(df), tbl = tbl))

#! -- END WELLS ----------------------------------------------------------------


#! -- TANKS --------------------------------------------------------------------

#! TANKS
df = pd.DataFrame()
p = tanks_path
tbl = 'TANKS'
id_name = tank_id_name

path = p
i = iWell(url=url+path, tbl=tbl)
i.request_entity()
i.df = i.df.rename(columns={'id': 'tank_id'
							,'name' : 'tank_name'
							,'type' : 'tank_type'
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							})
i.entity_to_db()
tanks = i.df['tank_id']
print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))

#! TANK_READINGS
df = pd.DataFrame()
p = readings_path
ids = tanks.values.tolist()
tbl = 'TANK_READINGS'
id_name = reading_id_name

for tank_id in ids:
	path = p.format(tank_id=tank_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	i.df[tank_id_name] = tank_id
	i.df.rename(columns={'id': id_name
						,'updated_at' : 'updated_iwell'
						}, inplace=True)
	df = df.append(i.df, sort=True)
	print('     {path} - {count} records'.format(path=path,
												 count=len(i.df))) if len(i.df) > 0 else None

i.df = df
i.entity_to_db()
tank_readings = i.df[[id_name, tank_id_name]].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))

#! RUN_TICKETS
df = pd.DataFrame()
p = reading_run_tickets_path
ids = tank_readings.values.tolist()
tbl = 'RUN_TICKETS'
id_name = run_ticket_id_name

for reading_id, tank_id in ids:
	path = p.format(tank_id=tank_id, reading_id=reading_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	i.df['tank_id'] = tank_id
	i.df['reading_id'] = reading_id
	i.df = i.df.rename(columns={'id': 'run_ticket_id'
							,'date' : 'reading_date'
							,'type' : 'product_type'
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							})
	df = df.append(i.df, sort=True)
	print('     {path} - {count} records'.format(path=path,
												 count=len(i.df))) if len(i.df) > 0 else None

i.df = df
i.entity_to_db()
run_tickets = i.df[[id_name, 'tank_id', 'reading_id']].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# #! RUN_TICKET -- Get Single Run Ticket
# df = pd.DataFrame()
# p = run_tickets_path
# ids = tank_reading_run_tickets.values.tolist()
# tbl = 'RUN_TICKETS'
# id_name = run_ticket_id_name

# # run_ticket_id, tank_id, reading_id
# for run_ticket_id, tank_id, reading_id in ids:
#     path = p.format(tank_id = tank_id, reading_id = reading_id, run_ticket_id = run_ticket_id)
#     i = iWell(url = url+path, tbl = tbl)
#     i.request_entity(orient = 'index')
#     i.df[tank_id_name] = tank_id
#     i.df[reading_id_name] = reading_id
#     i.df.rename(columns = {'id': id_name}, inplace = True)
#     i.df = i.df.reset_index().drop(columns=['index'])
#     df = df.append(i.df, sort = True)
#     print('{path} - {count} records'.format(path = path, count = len(i.df)))

# i.df = df
# i.entity_to_db()
# run_tickets = i.df[[id_name, tank_id_name, reading_id_name, run_ticket_id_name]].astype('int')
# print('{tbl} - {count} records loaded'.format(count=len(df), tbl = tbl))

#! -- END TANKS ----------------------------------------------------------------

#! -- METERS -------------------------------------------------------------------


#! METERS
df = pd.DataFrame()
p = meters_path
ids = wells.values.tolist()
tbl = 'METERS'
id_name = meter_id_name

for well_id in ids:
	path = p.format(well_id=well_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	if i.df is not None and not i.df.empty:
		i.df[well_id_name] = well_id
		i.df = i.df.rename(columns={'id': 'meter_id'
								,'date' : 'reading_date'
								,'type' : 'product_type'
								,'name' : 'meter_name'
								,'order' : 'meter_order'
								,'created_at' : 'created_iwell'
								,'updated_at' : 'updated_iwell'
								})
		df = df.append(i.df, sort=True)
		print('     {path} - {count} records'.format(path=path, count=len(i.df)))
	else:
		print('     {path} - skipped'.format(path=path, count=0))

i.df = df
i.entity_to_db()
if i.df is not None and not i.df.empty:
	meters = i.df[['meter_id', 'well_id']].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


#! METER_READINGS
df = pd.DataFrame()
p = meter_readings_path
ids = meters.values.tolist()
tbl = 'METER_READINGS'
id_name = meter_reading_id_name

for meter_id, well_id in ids:
	path = p.format(meter_id=meter_id, well_id=well_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	if i.df is not None and not i.df.empty:
		i.df[meter_id_name] = meter_id
		i.df[well_id_name] = well_id
		i.df.rename(columns={'id': id_name
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							}, inplace=True)
		df = df.append(i.df, sort=True)
		print('     {path} - {count} records'.format(path=path,
													count=len(i.df))) if len(i.df) > 0 else None
	else:
		print('     {path} - skipped'.format(path=path, count=0))

i.df = df
i.entity_to_db()
if i.df is not None and not i.df.empty:
	meter_readings = i.df[[id_name, well_id_name]].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


#! -- END METERS ---------------------------------------------------------------



#! -- PRODUCTION ---------------------------------------------------------------


# import pytz

# i.df[i.df.prod_datetime.max() == i.df.prod_datetime].T
# local = i.df.prod_datetime.max().tz_localize(pytz.timezone('US/Central'))
# dir(pd.Timestamp.tz_localize)
 


# pytz.timezone('UTC')._utcoffset
# # usc = pytz.timezone('US/Central')._utcoffset

# pd.Timestamp.tz_localize(i.df.prod_datetime.iloc[0], usc)

# pd.Timestamp.fromtimestamp(1538750942)


# pd.Timestamp.to_datetime64(local)
# print(pd.Timestamp.to_pydatetime(local))
# local
# well_id = 14714
# local = pd.read_json(r.text, orient='split',convert_dates = False)

# local.prod_datetime.apply(pd.Timestamp.fromtimestamp)



# i.df = local

# i.df[['prod_datetime','updated_iwell']] = i.df[['prod_datetime','updated_iwell']].apply(lambda t: [pd.Timestamp.fromtimestamp(x) for x in t])



#! PRODUCTION
df = pd.DataFrame()
p = production_path
ids = wells.values.tolist()
tbl = 'PRODUCTION_DAILY'
id_name = production_id_name

for well_id in ids:
	path = p.format(well_id=well_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	if i.df is not None and not i.df.empty:
		i.df['well_id'] = well_id
		i.df.rename(columns={'id': 'production_id'
							,'production_time' : 'prod_datetime'
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							}, inplace=True)
		i.df.drop(columns=['date'], inplace=True)
		df = df.append(i.df, sort=True)
		print('     {path} - {count} records'.format(path=path, count=len(i.df)))
	else:
		print('     {path} - skipped'.format(path=path, count=0))

i.df = df
i.entity_to_db()
if i.df is not None and not i.df.empty:
	production = i.df[['production_id', 'well_id']].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# prod = i.df
# prod.dtypes

# prod.head()

# p = prod.set_index('prod_datetime')
# p = p[p.well_id == 17417][['oil', 'gas', 'water']]
# p2 = p
# p = p.resample('H').ffill()

# p['oil2'] = p.oil/ 24

# p

# p.resample('D').sum()
# p2

# p[p.index.month == p.index.max().month]




# pd.DataFrame.drop

# x = i.df.duplicated(subset = ['production_id'])
# x[~x]


#! -- END PRODUCTION -----------------------------------------------------------


#! -- WELL GROUPS --------------------------------------------------------------

#! WELL_GROUPS
df = pd.DataFrame()
p = well_groups_path
tbl = 'WELL_GROUPS'
id_name = well_groups_id_name

path = p
i = iWell(url=url+path, tbl=tbl)
i.request_entity(njson = True)
if i.df is not None and not i.df.empty:
	well_ids = pd.DataFrame(i.df['wells.data'].values.tolist()[0]).rename({0: 'well_id'}, axis = 1)
	well_ids['well_group_id'] = i.df.id[0]
	# i.df = pd.concat([i.df, well_ids], axis = 1).ffill().drop('wells.data', axis = 1)
	i.df.created_at = i.df.created_at.apply(datetime.utcfromtimestamp)
	i.df.latest_production_time = i.df.latest_production_time.apply(datetime.utcfromtimestamp)
	i.df.updated_at = i.df.updated_at.apply(datetime.utcfromtimestamp)
	i.df = i.df.rename(columns={'id': 'group_id'
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							,'name' : 'group_name'
							,'latest_production_time' : 'group_latest_production_time'
							})
	i.df = i.df.drop(columns = ['wells.data',
								# ,'is_active'
								# ,'latest_production_time'
								# ,''
								], axis = 1)
	i.entity_to_db()
	well_groups = i.df['group_id']
	print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))
else:
	print('     {path} - skipped'.format(path=path, count=0))


#! WELL_GROUP_WELLS
df = pd.DataFrame()
p = well_group_wells_path
ids = well_groups.values.tolist()
tbl = 'WELL_GROUP_WELLS'
id_name = 'well_id'

for group_id in ids:
	path = p.format(group_id=group_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	if i.df is not None and not i.df.empty:
		i.df['group_id'] = group_id
		i.df.rename(columns={'id': 'well_id'
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							}, inplace=True)
		df = df.append(i.df, sort=True)
		print('     {path} - {count} records'.format(path=path,
													count=len(i.df))) if len(i.df) > 0 else None
	else:
		print('     {path} - skipped'.format(path=path, count=0))
			
i.df = df[['group_id', 'well_id', 'created_iwell', 'updated_iwell']]
i.entity_to_db()
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# i.df.to_sql(i.tbl, i.engine, if_exists='append', index=false)


#! -- END WELL GROUPS ----------------------------------------------------------


#! -- FIELDS -------------------------------------------------------------------

#! FIELDS
df = pd.DataFrame()
p = fields_path
tbl = 'FIELDS'
id_name = field_id_name

path = p
i = iWell(url=url+path, tbl=tbl)
i.request_entity()
i.df.rename(columns={'id': id_name
							,'name' : 'field_name'
							,'order' : 'field_order'
							,'type' : 'field_type'
							,'unit' : 'field_unit'
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							}, inplace=True)
i.entity_to_db()
fields = i.df[id_name]
print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))

#! FIELDS_BY_WELL
df = pd.DataFrame()
p = well_fields_path
ids = wells.values.tolist()
tbl = 'FIELDS_BY_WELL'
id_name = field_id_name

for well_id in ids:
	path = p.format(well_id=well_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	if i.df is not None and not i.df.empty:
		i.df[well_id_name] = well_id
		i.df.rename(columns={'id': id_name
							,'name' : 'field_name'
							,'order' : 'field_order'
							,'type' : 'field_type'
							,'unit' : 'field_unit'
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							}, inplace=True)
		df = df.append(i.df, sort=True)
		print('     {path} - {count} records'.format(path=path,
													count=len(i.df))) if len(i.df) > 0 else None
	else:
		print('     {path} - skipped'.format(path=path, count=0))
			
i.df = df
i.entity_to_db()
if i.df is not None and not i.df.empty:
	well_fields = i.df[[id_name, well_id_name]].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))

#! FIELD_VALUES
df = pd.DataFrame()
p = well_field_values_path
ids = well_fields.values.tolist()
tbl = 'FIELD_VALUES'
id_name = field_values_id_name

for field_id, well_id in ids:
	path = p.format(well_id=well_id, field_id=field_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	if i.df is not None and not i.df.empty:
		i.df[well_id_name] = well_id
		i.df[field_id_name] = field_id
		i.df.rename(columns={'id': id_name
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							}, inplace=True)
		df = df.append(i.df, sort=True)
		print('     {path} - {count} records'.format(path=path,
													count=len(i.df))) if len(i.df) > 0 else None

i.df = df
i.entity_to_db()
if i.df is not None and not i.df.empty:
	field_values = i.df[[id_name, well_id_name, field_id_name]].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


#! -- END FIELDS ---------------------------------------------------------------



# #! -- VALIDATION RULES ---------------------------------------------------------

# # ? Validation rules by Well
# #! VALIDATION_RULES
# df = pd.DataFrame()
# p = validation_rules_path
# ids = wells.values.tolist()
# tbl = 'VALIDATION_RULES'
# id_name = field_id_name

# for well_id in ids:
# 	path = p.format(well_id=well_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df[well_id_name] = well_id
# 		i.df.rename(columns={'id': id_name}, inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path,
# 													count=len(i.df))) if len(i.df) > 0 else None
# 	else:
# 		print('     {path} - skipped'.format(path=path, count=0))
			
# i.df = df
# i.entity_to_db()
# if i.df is not None and not i.df.empty:
# 	well_fields = i.df[[id_name, well_id_name]].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))

# #! -- END VALIDATION RULES -----------------------------------------------------



#! -- WELL_NOTES ---------------------------------------------------------------

# ? notes
#! WELL_NOTES
df = pd.DataFrame()
p = well_notes_path
ids = wells.values.tolist()
tbl = 'WELL_NOTES'
id_name = note_id_name

for well_id in ids:
	path = p.format(well_id=well_id)
	i = iWell(url=url+path, tbl=tbl)
	i.request_entity()
	if i.df is not None and not i.df.empty:
		i.df[well_id_name] = well_id
		i.df.rename(columns={'id': id_name
							,'created_at' : 'created_iwell'
							,'updated_at' : 'updated_iwell'
							}, inplace=True)
		df = df.append(i.df, sort=True)
		print('     {path} - {count} records'.format(path=path,
													count=len(i.df))) if len(i.df) > 0 else None
	else:
		print('     {path} - skipped'.format(path=path, count=0))
			
i.df = df
i.entity_to_db()
if i.df is not None and not i.df.empty:
	well_fields = i.df[[id_name, well_id_name]].astype('int')
print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))

#! -- END WELL_NOTES -----------------------------------------------------------


# ? Testing

# for id, refid in ids:
#     print('{}---{}'.format(id, refid))

# i.df.T

# i.df.dtypes

# i.df.reset_index().drop(columns=['index'])


# path = url+welltanks_path

r = requests.get(url+path, headers={'Authorization': i.getBearer()})
pprint(r.json())
i.request_entity(orient = 'index')

pd.read_json(r.text)




pd.DataFrame(i.df2['wells.data'].values.tolist()[0]).dtypes

i.df2.T

i.df.T

# well_id = 16768

# path = p.format(well_id = well_id)
# i = iWell(url = url+path, tbl = tbl)
# i.request_entity()
# if i.df is not None and not i.df.empty:
#     i.df[well_id_name] = well_id
#     i.df.rename(columns = {'id': id_name}, inplace = True)
#     df = df.append(i.df, sort = True)
#     print('{path} - {count} records'.format(path = path, count = len(i.df)))
# else:
#     print('{path} - skipped'.format(path = path, count = 0))


# type(x)


# pprint(dir(response))
# pprint(response.json())

# df = pd.DataFrame.from_records(response.json())
# df.head()
# pd.DataFrame.from_dict(response.json()['data'])
