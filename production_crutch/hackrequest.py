

import sys, os
sys.path.insert(0, os.path.abspath('../src'))


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

def addsince(path, since = '1980-01-01'):
	return '?since={}'.format(int(pd.Timestamp(since).timestamp()))

production_path = '/wells/{well_id}/production'
production_path = production_path + addsince(production_path)

well_id_name = 'well_id'
production_id_name = 'production_id'

wells_path = '/wells'
wells_path = wells_path + addsince(wells_path)

class iWell(object):
	# TODO: Add Requestor
	# TODO: Add database table
	
	cfg = Config('config.yaml')
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

	def get_wells(self):
		"""Wrapper for request wells"""
		#! WELLS
		df = pd.DataFrame()
		p = wells_path
		tbl = 'WELLS'
		id_name = 'well_id'

		# path = p
		# i = iWell(url=url+path, tbl=tbl)
		i.request_entity()
		i.df = i.df.rename(columns={'id': 'well_id'
									,'name' : 'well_name'
									,'type' : 'well_type'
									,'updated_at' : 'updated_iwell'
									,'created_at' : 'created_iwell'
									,'alias' : 'well_alias'
									})


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


def getProduction(ids):
	#! PRODUCTION
	df = pd.DataFrame()
	p = production_path
	# ids = well_ids
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
