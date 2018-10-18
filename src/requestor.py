
import os
try:
    os.chdir('src')

except:
    pass

finally:
    os.getcwd()

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

# client_id = "KTDMpqhGyBMhnRDB"
# client_secret = "gYFRiXRtMN0fDYTDPUDYOk1RAbPz44Bu"
# username = 'data@driftwoodenergy.com'
# password = '7haYrAaFqTwS'

# _properties['client_id'] = "KTDMpqhGyBMhnRDB"
# _properties['client_secret'] = "gYFRiXRtMN0fDYTDPUDYOk1RAbPz44Bu"
# _properties['username'] = 'data@driftwoodenergy.com'
# _properties['password'] = '7haYrAaFqTwS'
# _properties['token_path']  = '/oauth2/access-token'

pd.options.display.max_rows = None
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('large_repr', 'truncate')
pd.set_option('precision',2)

# TODO: Move to main?
_properties = Config('../config.yaml')

# for k in _properties['endpoints']:
# 	print(type(k))
# 	_properties['endpoints'][k]['last_success']=datetime.now() - timedelta(days = 7)
	



class iwell_api(object):
	url = _properties['url']
	
	
	def __init__(self, endpoint_name: str):
		self.headers = {
			'Authorization': self.getBearer()
		}
		self.df = pd.DataFrame()
		self.endpoint_name = endpoint_name
		self.uris = {}

		self.endpoint = _properties['endpoints'][endpoint_name]['path']
		self.aliases = _properties['endpoints'][endpoint_name]['aliases']
		self.exclusions = _properties['endpoints'][endpoint_name]['exclude']
		self.njson = _properties['endpoints'][endpoint_name]['normalize']
		self.keys = _properties['endpoints'][endpoint_name]['keys']

	@classmethod
	def reload_properties(cls):
		"""refresh property attributes
		"""
		_properties = Config('../config.yaml')

	@classmethod
	def cache_properties(cls):
		"""refresh property attributes
		"""
		_properties['cached_at'] = datetime.now()

	@classmethod
	def _getAccessToken(cls):
		# FIXME: Fetching new token tries to attach to str and fails
		"""Fetch a new access token from the provider using OAuth2"""
		# https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
		oauth = OAuth2Session(
			client=LegacyApplicationClient(client_id=_properties['client_id']))

		return oauth.fetch_token(
			token_url= cls.url + _properties['token_path']
			, username=_properties['username']
			, password=_properties['password']
			, client_id=_properties['client_id']
			, client_secret=_properties['client_secret']
		)

	@classmethod
	def _token_saver(cls, response_token):
		"""Save response token and token expiration date to configuration file.
		Arguments:
			response_token {dict} -- oauth response object
		Returns:
			str -- response token as string
		"""

		_properties["token"] = response_token["access_token"]
		_properties["token_expiration"] = (
			datetime.utcfromtimestamp(response_token['expires_at']))

		return response_token

	@classmethod
	def getAccessToken(cls, force = False):
		""" Checks if saved token is still valid"""
		token = _properties["token"]
		expiration = _properties["token_expiration"]

		# if force change flag is False
		if not force:
			# if expiration date exists and is a datetime
			if expiration is not None and isinstance(expiration, datetime):
				# if current time is < time of expiration minus one day
				if datetime.now() < expiration - timedelta(days=1):
					# print('Current token is valid.')
					return token

		# Token wasn't valid. Return new token
		print('Retrieved new token.')
		return cls._token_saver(cls._getAccessToken())['token']

	@classmethod
	def getBearer(cls):
		"""Returns bearer authorization string for inclusion
			in request header.
		Returns:
			str -- bearer string
		"""

		return "Bearer " + cls.getAccessToken()

	def add_since(self, since: datetime = None) -> str:
		"""Append ?since clause to endpoint string. Default settings pull all data.
		
		Arguments:
			endpoint {str} -- Provider URI or endpoint
		
		Keyword Arguments:
			since {datetime} -- datetime object (default: 1420107010)
		
		Returns:
			[str] -- endpoint appended with since clause.
							ex: "endpoint?since=32342561"
		"""
		
		if since:
			return '?since={}'.format(int(since.timestamp()))
		else:
			return ''


	def get_last_success(self):
		"""Get last successful runtime of this endpoint
		
		Returns:
			[datetime] -- last successful runtime
		"""

		return _properties['endpoints'][self.endpoint_name]['last_success']


	def set_last_success(self):
		"""Set last successful runtime of this endpoint
		
		Returns:
			None
		"""

		_properties['endpoints'][self.endpoint_name]['last_success'] = datetime.now()
		self.cache_properties()


	def get_last_failure(self):
		"""Get last failed runtime of this endpoint
		
		Returns:
			[datetime] -- last successful runtime
		"""

		return _properties['endpoints'][self.endpoint_name]['last_failure']


	def set_last_failure(self):
		"""Set last failed runtime of this endpoint
		
		Returns:
			None
		"""
		
		_properties['endpoints'][self.endpoint_name]['last_failure'] = datetime.now()
		self.cache_properties()

	def request_entity(self, delta: datetime = None):
		"""Generic vehicle for sending GET requests
		
		Keyword Arguments:
			orient {str} -- specify orientation of resonse records (default: {'split'})
			delta {datetime} -- if None, all data is requested. if datetime is specified, data updated since the specified date will be requested.
		"""

		# if delta is not a valid datetime, log error and return
		if delta and not isinstance(delta, datetime):
			# TODO: Add Sentry
			print('Invalid function parameter "delta": not a valid datetime')
			return None

		response = None
		# build uri
		uri = self.url+self.endpoint
		# append date limitation, if supplied
		uri = uri + self.add_since(delta) if delta else uri
		print('{}'.format(uri))
		try:

			response = requests.get(uri, headers=self.headers)
			if response.ok:

				if self.njson:
					self.df = pd.io.json.json_normalize(response.json()['data'])
					
				else:
					self.df = pd.read_json(response.text, orient='split')
					
				self.set_last_success()
				
				print('		{0} - {1} -- Downloaded {2} records'.format(self.__class__.__name__
																, self.endpoint_name
																, self.download_count()
																))
			else:
				print('     {path} - {message}'.format(
					path=response.request.path_url, message=response.json()['error']['message']))
				self.df = None
				self.set_last_failure()

		except Exception as e:
			#TODO: Add Sentry
			print(e)
			print('     Entity not retrieved.')
			self.df = None
			self.set_last_failure()

	def request_uri(self, uri: str, ids: dict = None):
		"""Generic vehicle for sending GET requests
		
		Keyword Arguments:
			orient {str} -- specify orientation of resonse records (default: {'split'})
			delta {datetime} -- if None, all data is requested. if datetime is specified, data updated since the specified date will be requested.
		"""

		if not ids:
			ids = {}


		response = None
		
		# print('Requesting: {}'.format(uri))
		try:

			response = requests.get(uri, headers=self.headers)
			if response.ok:

				# Append responses to dataframe
				if self.njson:
					response_df = pd.io.json.json_normalize(response.json()['data'])
					
				else:
					response_df = pd.read_json(response.text, orient='split')
					
				# Add ids as columns to dataframe
				for id, val in ids.items():
					if id not in response_df.columns:
						response_df[id] = val
				
				# Append response to object dataframe of responses
				self.df = self.df.append(response_df, sort = True)

				count = response_df.count().max()
				count = count if not pd.isna(count) else 0

				self.set_last_success()

				print('		{0} - {1} -- Downloaded {2} records'.format(self.__class__.__name__
																, uri.replace(self.url, '')
																, count
																))
			else:
				print('		{obj} - {path} -- {message}'.format(obj = self.__class__.__name__
												, path=response.request.path_url
												, message=response.json()['error']['message']))
				self.set_last_failure()
			# try:
			# 	del self.uris[uri]
			# except Exception as e:
			# 	print(e)


		except Exception as e:
			#TODO: Add Sentry
			print(e)
			print('     Entity not retrieved.')
			self.set_last_failure()

	def request_uris(self):
		for uri, ids in self.uris.items():
			self.request_uri(uri, ids)
		
		self.downloaded_status()
		self.uris = {}

	def parse_response(self):

		# if self.aliases is not None:
		self.df = self.df.rename(columns = self.aliases)

		# Fix timezones
		self.df[list(self.df.select_dtypes('datetime').columns)] = self.df.select_dtypes('datetime').apply(lambda x: x.dt.tz_localize('utc')).apply(lambda x: x.dt.tz_convert('US/Central'))

		# Fill NAs
		self.df = self.df.fillna(0)

		# if self.exclusions is not None:
		try:
			self.df = self.df.drop(columns = self.exclusions)
		except Exception as e:
			print(e)


	def downloaded_status(self):
		"""Return rowcount of downloads
		"""

		if self.df is not None:
			n = self.df.count().max()
		else:
			n = 0

		print('		{0} - {1} -- Downloaded {2} records'.format(self.__class__.__name__
															, self.endpoint_name
															, n
															))
		return n


	def keys(self):
		return list(self.df[self.aliases['id']].values)


	def keyedkeys(self):
		return self.df[[self.aliases['id']]].to_dict('records')


	def build_uri(self, well_id = None, group_id = None, tank_id = None
				, run_ticket_id = None, meter_id = None, field_id = None
				, reading_id = None, note_id = None, delta = None):
		"""Wrapper to build a uri from a set of identifiers
		
		Arguments:
			well_id {str} (optional) --
			group_id {str} (optional) --
			tank_id {str} (optional) --
			run_ticket_id {str} (optional) --
			meter_id {str} (optional) --
		
		Returns:
			{str} -- url endpoint
		"""

		ids = {
			'well_id' : well_id
			, 'group_id' : group_id
			, 'tank_id' : tank_id
			, 'run_ticket_id' : run_ticket_id
			, 'meter_id' : meter_id
			, 'field_id' : field_id
			, 'reading_id' : reading_id
			, 'note_id' : note_id
			}

		uri =  self.url+self.endpoint.format(**ids)
		self.uris[uri] = {id: val for id, val in ids.items() if val is not None}
		return uri


	def build_uris(self, ids: list, delta = None):
		"""Wrapper to build multiple uris from a list of ids
		
		Arguments:
			ids {list} -- list of identifiers
		
		Returns:
			{list} -- list of populated uri endpoints
		"""
		[self.build_uri(**x, delta = delta) for x in ids]




def main():
	pass

if __name__ == '__main__':
	main()



# headers = {
# 			'Authorization': iwell_api.getBearer()
# 		}

# response = None
# # build uri
# uri = 'https://api.iwell.info/v1'+'/monitor'
# # append date limitation, if supplied
# # uri = uri + self.add_since(delta) if delta else uri
# print('{}'.format(uri))

# response = requests.get(uri, headers=headers)
# if response.ok:

# 	if self.njson:
# 		df = pd.io.json.json_normalize(response.json()['data'])
		
# 	else:
# 		df = pd.read_json(response.text, orient='split')


# requests.get(uri, headers=headers).prepare()


# wells = iwell(_properties['endpoints']['wells'])

# wells.request_entity()

# df = wells.df

# iwell.cache_properties()





# df = pd.DataFrame()
# p = wells_path
# tbl = 'WELLS'
# id_name = well_id_name

# path = p
# i = iWell(url=url+path, tbl=tbl)
# i.request_entity()
# i.df = i.df.rename(columns={'id': id_name
# 							,'name' : 'well_name'
# 							,'type' : 'well_type'
# 							,'updated_at' : 'updated_iwell'
# 							,'created_at' : 'created_iwell'
# 							,'alias' : 'well_alias'
# 							})
# i.entity_to_db()
# wells = i.df[id_name]
# print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))







# if __name__ == '__main__':
# 	pass

# # i = iWell()

# # wells = i.request_wells()
# # i.temp_wells_to_db()


# #FIXME:

# # FIXME: ENRICH WITH DEO DATA

# # FIXME: ADD FOREIGN KEYS TO DATABASE

# # FIXME: Normalize production across 24 hours



# #!----------------------------------------------------------------------------!#


# # def addsince(path, since = '1980-01-01'):
# # 	return '?since={}'.format(int(pd.Timestamp(since).timestamp()))








# well_id_name = 'well_id'
# tank_id_name = 'tank_id'
# reading_id_name = 'reading_id'
# run_ticket_id_name = 'run_ticket_id'
# meter_id_name = 'meter_id'
# well_groups_id_name = 'well_group_id'
# field_id_name = 'field_id'
# field_values_id_name = 'value_id'
# production_id_name = 'production_id'
# meter_reading_id_name = 'meter_reading_id'
# validation_id_name = 'validation_id'
# note_id_name = 'note_id'

# #! -- WELLS --------------------------------------------------------------------

# #! WELLS
# df = pd.DataFrame()
# p = wells_path
# tbl = 'WELLS'
# id_name = well_id_name

# path = p
# i = iWell(url=url+path, tbl=tbl)
# i.request_entity()
# i.df = i.df.rename(columns={'id': id_name
# 							,'name' : 'well_name'
# 							,'type' : 'well_type'
# 							,'updated_at' : 'updated_iwell'
# 							,'created_at' : 'created_iwell'
# 							,'alias' : 'well_alias'
# 							})
# i.entity_to_db()
# wells = i.df[id_name]
# print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))

# #! WELL TANKS
# df = pd.DataFrame()
# p = '/wells/{well_id}/tanks'
# ids = wells.values.tolist()
# tbl = 'WELL_TANKS'
# id_name = tank_id_name

# for well_id in ids:
# 	path = p.format(well_id=well_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	print(i.df)
# 	if i.df is not None and not i.df.empty:
# 		i.df[well_id_name] = well_id
# 		i.df.rename(columns={'id': 'tank_id'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path,
# 													count=len(i.df))) if len(i.df) > 0 else None

# i.df = df['tank_id','well_id']
# i.entity_to_db()
# tank_readings = i.df[['tank_id', 'well_id']].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# #! -- END WELLS ----------------------------------------------------------------


# #! -- TANKS --------------------------------------------------------------------

# #! TANKS
# df = pd.DataFrame()
# p = tanks_path
# tbl = 'TANKS'
# id_name = tank_id_name

# path = p
# i = iWell(url=url+path, tbl=tbl)
# i.request_entity()
# i.df = i.df.rename(columns={'id': 'tank_id'
# 							,'name' : 'tank_name'
# 							,'type' : 'tank_type'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							})
# i.entity_to_db()
# tanks = i.df['tank_id']
# print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))

# #! TANK_READINGS
# df = pd.DataFrame()
# p = readings_path
# ids = tanks.values.tolist()
# tbl = 'TANK_READINGS'
# id_name = reading_id_name

# for tank_id in ids:
# 	path = p.format(tank_id=tank_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df[tank_id_name] = tank_id
# 		i.df.rename(columns={'id': id_name
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path,
# 													count=len(i.df))) if len(i.df) > 0 else None

# i.df = df
# i.entity_to_db()
# tank_readings = i.df[[id_name, tank_id_name]].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))

# #! RUN_TICKETS
# df = pd.DataFrame()
# p = reading_run_tickets_path
# ids = tank_readings.values.tolist()
# tbl = 'RUN_TICKETS'
# id_name = run_ticket_id_name

# for reading_id, tank_id in ids:
# 	path = p.format(tank_id=tank_id, reading_id=reading_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	i.df['tank_id'] = tank_id
# 	i.df['reading_id'] = reading_id
# 	i.df = i.df.rename(columns={'id': 'run_ticket_id'
# 							,'date' : 'reading_date'
# 							,'type' : 'product_type'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							})
# 	df = df.append(i.df, sort=True)
# 	print('     {path} - {count} records'.format(path=path,
# 												 count=len(i.df))) if len(i.df) > 0 else None

# i.df = df
# i.entity_to_db()
# run_tickets = i.df[[id_name, 'tank_id', 'reading_id']].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))



# #! -- END TANKS ----------------------------------------------------------------

# #! -- METERS -------------------------------------------------------------------


# #! METERS
# df = pd.DataFrame()
# p = meters_path
# ids = wells.values.tolist()
# tbl = 'METERS'
# id_name = meter_id_name

# for well_id in ids:
# 	path = p.format(well_id=well_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df[well_id_name] = well_id
# 		i.df = i.df.rename(columns={'id': 'meter_id'
# 								,'date' : 'reading_date'
# 								,'type' : 'product_type'
# 								,'name' : 'meter_name'
# 								,'order' : 'meter_order'
# 								,'created_at' : 'created_iwell'
# 								,'updated_at' : 'updated_iwell'
# 								})
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path, count=len(i.df)))
# 	else:
# 		print('     {path} - skipped'.format(path=path, count=0))

# i.df = df
# i.entity_to_db()
# if i.df is not None and not i.df.empty:
# 	meters = i.df[['meter_id', 'well_id']].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# #! METER_READINGS
# df = pd.DataFrame()
# p = meter_readings_path
# ids = meters.values.tolist()
# tbl = 'METER_READINGS'
# id_name = meter_reading_id_name

# for meter_id, well_id in ids:
# 	path = p.format(meter_id=meter_id, well_id=well_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df[meter_id_name] = meter_id
# 		i.df[well_id_name] = well_id
# 		i.df.rename(columns={'id': id_name
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path,
# 													count=len(i.df))) if len(i.df) > 0 else None
# 	else:
# 		print('     {path} - skipped'.format(path=path, count=0))

# i.df = df
# i.entity_to_db()
# if i.df is not None and not i.df.empty:
# 	meter_readings = i.df[[id_name, well_id_name]].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# #! -- END METERS ---------------------------------------------------------------



# #! -- PRODUCTION ---------------------------------------------------------------


# # import pytz

# # i.df[i.df.prod_datetime.max() == i.df.prod_datetime].T
# # local = i.df.prod_datetime.max().tz_localize(pytz.timezone('US/Central'))
# # dir(pd.Timestamp.tz_localize)
 


# # pytz.timezone('UTC')._utcoffset
# # # usc = pytz.timezone('US/Central')._utcoffset

# # pd.Timestamp.tz_localize(i.df.prod_datetime.iloc[0], usc)

# # pd.Timestamp.fromtimestamp(1538750942)


# # pd.Timestamp.to_datetime64(local)
# # print(pd.Timestamp.to_pydatetime(local))
# # local
# # well_id = 14714
# # local = pd.read_json(r.text, orient='split',convert_dates = False)

# # local.prod_datetime.apply(pd.Timestamp.fromtimestamp)



# # i.df = local

# # i.df[['prod_datetime','updated_iwell']] = i.df[['prod_datetime','updated_iwell']].apply(lambda t: [pd.Timestamp.fromtimestamp(x) for x in t])



# #! PRODUCTION
# df = pd.DataFrame()
# p = production_path
# ids = wells.values.tolist()
# tbl = 'PRODUCTION_DAILY'
# id_name = production_id_name

# for well_id in ids:
# 	path = p.format(well_id=well_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df['well_id'] = well_id
# 		i.df.rename(columns={'id': 'production_id'
# 							,'production_time' : 'prod_datetime'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# 		i.df.drop(columns=['date'], inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path, count=len(i.df)))
# 	else:
# 		print('     {path} - skipped'.format(path=path, count=0))

# i.df = df
# i.entity_to_db()
# if i.df is not None and not i.df.empty:
# 	production = i.df[['production_id', 'well_id']].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# # prod = i.df
# # prod.dtypes

# # prod.head()

# # p = prod.set_index('prod_datetime')
# # p = p[p.well_id == 17417][['oil', 'gas', 'water']]
# # p2 = p
# # p = p.resample('H').ffill()

# # p['oil2'] = p.oil/ 24

# # p

# # p.resample('D').sum()
# # p2

# # p[p.index.month == p.index.max().month]




# # pd.DataFrame.drop

# # x = i.df.duplicated(subset = ['production_id'])
# # x[~x]


# #! -- END PRODUCTION -----------------------------------------------------------


# #! -- WELL GROUPS --------------------------------------------------------------

# #! WELL_GROUPS
# df = pd.DataFrame()
# p = well_groups_path
# tbl = 'WELL_GROUPS'
# id_name = well_groups_id_name

# path = p
# i = iWell(url=url+path, tbl=tbl)
# i.request_entity(njson = True)
# if i.df is not None and not i.df.empty:
# 	well_ids = pd.DataFrame(i.df['wells.data'].values.tolist()[0]).rename({0: 'well_id'}, axis = 1)
# 	well_ids['well_group_id'] = i.df.id[0]
# 	# i.df = pd.concat([i.df, well_ids], axis = 1).ffill().drop('wells.data', axis = 1)
# 	i.df.created_at = i.df.created_at.apply(datetime.utcfromtimestamp)
# 	i.df.latest_production_time = i.df.latest_production_time.apply(datetime.utcfromtimestamp)
# 	i.df.updated_at = i.df.updated_at.apply(datetime.utcfromtimestamp)
# 	i.df = i.df.rename(columns={'id': 'group_id'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							,'name' : 'group_name'
# 							,'latest_production_time' : 'group_latest_production_time'
# 							})
# 	i.df = i.df.drop(columns = ['wells.data',
# 								# ,'is_active'
# 								# ,'latest_production_time'
# 								# ,''
# 								], axis = 1)
# 	i.entity_to_db()
# 	well_groups = i.df['group_id']
# 	print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))
# else:
# 	print('     {path} - skipped'.format(path=path, count=0))


# #! WELL_GROUP_WELLS
# df = pd.DataFrame()
# p = well_group_wells_path
# ids = well_groups.values.tolist()
# tbl = 'WELL_GROUP_WELLS'
# id_name = 'well_id'

# for group_id in ids:
# 	path = p.format(group_id=group_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df['group_id'] = group_id
# 		i.df.rename(columns={'id': 'well_id'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path,
# 													count=len(i.df))) if len(i.df) > 0 else None
# 	else:
# 		print('     {path} - skipped'.format(path=path, count=0))
			
# i.df = df[['group_id', 'well_id', 'created_iwell', 'updated_iwell']]
# i.entity_to_db()
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# # i.df.to_sql(i.tbl, i.engine, if_exists='append', index=false)


# #! -- END WELL GROUPS ----------------------------------------------------------


# #! -- FIELDS -------------------------------------------------------------------

# #! FIELDS
# df = pd.DataFrame()
# p = fields_path
# tbl = 'FIELDS'
# id_name = field_id_name

# path = p
# i = iWell(url=url+path, tbl=tbl)
# i.request_entity()
# i.df.rename(columns={'id': id_name
# 							,'name' : 'field_name'
# 							,'order' : 'field_order'
# 							,'type' : 'field_type'
# 							,'unit' : 'field_unit'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# i.entity_to_db()
# fields = i.df[id_name]
# print('\n{tbl} - {count} records loaded\n'.format(count=len(i.df), tbl=tbl))

# #! FIELDS_BY_WELL
# df = pd.DataFrame()
# p = well_fields_path
# ids = wells.values.tolist()
# tbl = 'FIELDS_BY_WELL'
# id_name = field_id_name

# for well_id in ids:
# 	path = p.format(well_id=well_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df[well_id_name] = well_id
# 		i.df.rename(columns={'id': id_name
# 							,'name' : 'field_name'
# 							,'order' : 'field_order'
# 							,'type' : 'field_type'
# 							,'unit' : 'field_unit'
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path,
# 													count=len(i.df))) if len(i.df) > 0 else None
# 	else:
# 		print('     {path} - skipped'.format(path=path, count=0))
			
# i.df = df.dropna(subset = ['field_id'])
# i.entity_to_db()
# if i.df is not None and not i.df.empty:
# 	well_fields = i.df[[id_name, well_id_name]].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))

# # df[df.duplicated(subset = ['field_id'])]

# # help(df.duplicated)

# #! FIELD_VALUES
# df = pd.DataFrame()
# p = well_field_values_path
# ids = well_fields.values.tolist()
# tbl = 'FIELD_VALUES'
# id_name = field_values_id_name

# for field_id, well_id in ids:
# 	path = p.format(well_id=well_id, field_id=field_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df[well_id_name] = well_id
# 		i.df[field_id_name] = field_id
# 		i.df.rename(columns={'id': id_name
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
# 		df = df.append(i.df, sort=True)
# 		print('     {path} - {count} records'.format(path=path,
# 													count=len(i.df))) if len(i.df) > 0 else None

# i.df = df
# i.entity_to_db()
# if i.df is not None and not i.df.empty:
# 	field_values = i.df[[id_name, well_id_name, field_id_name]].astype('int')
# print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))


# #! -- END FIELDS ---------------------------------------------------------------



# # #! -- VALIDATION RULES ---------------------------------------------------------

# # # ? Validation rules by Well
# # #! VALIDATION_RULES
# # df = pd.DataFrame()
# # p = validation_rules_path
# # ids = wells.values.tolist()
# # tbl = 'VALIDATION_RULES'
# # id_name = field_id_name

# # for well_id in ids:
# # 	path = p.format(well_id=well_id)
# # 	i = iWell(url=url+path, tbl=tbl)
# # 	i.request_entity()
# # 	if i.df is not None and not i.df.empty:
# # 		i.df[well_id_name] = well_id
# # 		i.df.rename(columns={'id': id_name}, inplace=True)
# # 		df = df.append(i.df, sort=True)
# # 		print('     {path} - {count} records'.format(path=path,
# # 													count=len(i.df))) if len(i.df) > 0 else None
# # 	else:
# # 		print('     {path} - skipped'.format(path=path, count=0))
			
# # i.df = df
# # i.entity_to_db()
# # if i.df is not None and not i.df.empty:
# # 	well_fields = i.df[[id_name, well_id_name]].astype('int')
# # print('\n{tbl} - {count} records loaded\n'.format(count=len(df), tbl=tbl))

# # #! -- END VALIDATION RULES -----------------------------------------------------



# #! -- WELL_NOTES ---------------------------------------------------------------

# # ? notes
# #! WELL_NOTES
# df = pd.DataFrame()
# p = well_notes_path
# ids = wells.values.tolist()
# tbl = 'WELL_NOTES'
# id_name = note_id_name

# for well_id in ids:
# 	path = p.format(well_id=well_id)
# 	i = iWell(url=url+path, tbl=tbl)
# 	i.request_entity()
# 	if i.df is not None and not i.df.empty:
# 		i.df[well_id_name] = well_id
# 		i.df.rename(columns={'id': id_name
# 							,'created_at' : 'created_iwell'
# 							,'updated_at' : 'updated_iwell'
# 							}, inplace=True)
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

# #! -- END WELL_NOTES -----------------------------------------------------------


# # ? Testing

# # for id, refid in ids:
# #     print('{}---{}'.format(id, refid))

# # i.df.T

# # i.df.dtypes

# # i.df.reset_index().drop(columns=['index'])


# # path = url+welltanks_path

# # r = requests.get(url+path, headers={'Authorization': i.getBearer()})
# # pprint(r.json())
# # # i.request_entity(orient = 'index')

# # # pd.read_json(r.text)


# # i.url

# # r.text


# # pd.DataFrame(i.df2['wells.data'].values.tolist()[0]).dtypes

# # i.df2.T

# # i.df.T

# # well_id = 16768

# # path = p.format(well_id = well_id)
# # i = iWell(url = url+path, tbl = tbl)
# # i.request_entity()
# # if i.df is not None and not i.df.empty:
# #     i.df[well_id_name] = well_id
# #     i.df.rename(columns = {'id': id_name}, inplace = True)
# #     df = df.append(i.df, sort = True)
# #     print('{path} - {count} records'.format(path = path, count = len(i.df)))
# # else:
# #     print('{path} - skipped'.format(path = path, count = 0))


# # type(x)


# # pprint(dir(response))
# # pprint(response.json())

# # df = pd.DataFrame.from_records(response.json())
# # df.head()
# # pd.DataFrame.from_dict(response.json()['data'])
