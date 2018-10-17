
import os
try:
    os.chdir('src')

except:
    pass

finally:
    os.getcwd()

from requestor import *
from dbagents import *



# Setup

#! CLASSES in CAPS represent Driftwood_DB tables

#! Classes in CamelCase represent iWell objects

db = iwell_agent()
wells = iwell_api('wells')
prod = iwell_api('production')


#**
WELLS.session = db.Session()
PROD.session = db.Session()


#? Transport



#** Get wells from iWell
wells.request_entity(delta= (datetime.now() - timedelta(days = 1)))

#** Clean up wells from iWell
wells.parse_response()

#** Merge records into session
WELLS.merge_records(wells.df)

#** Get affected row counts
WELLS.get_session_state()

#** Persist changes to database
WELLS.persist()


#** Get wells from iWell
prod.request_entity(delta= (datetime.now() - timedelta(days = 1)))

#** Clean up wells from iWell
prod.parse_response()

#** Merge records into session
PROD.merge_records(prod.df)

#** Get affected row counts
PROD.get_session_state()

#** Persist changes to database
PROD.persist()


# FIXME: Updating on delta is not working


if 1 = 0:
    pd.Timestamp(datetime.now()).timestamp()
    wells.add_since(datetime.now())
    wells.endpoint +'?since={}'.format(int(pd.Timestamp(datetime.now()).timestamp()))
    # TODO: START HERE -> Get "merge" method from Flowback

    #TODO: Merge -> load inserts -> load updates


    wells.df.alias
    wells.df.updated_at


    headers = {
                'Authorization': wells.getBearer()
            }
    delta = (datetime.now() - timedelta(days = 1))
    uri = wells.url+wells.endpoint
    uri = uri + '?since={}'.format(datetime.now().timestamp())
    r = requests.get(uri, headers=headers)

    '?since={}'.format(int(pd.Timestamp(datetime.now()).timestamp()))

    datetime.now().timestamp()


    r.json()

    r.url

    datetime.now().timestamp()
    datetime.strptime('1970-01-01', '%Y-%m-%d')

    datetime.fromtimestamp(1539146828)

prod.endpoint.format(prod_id = 'XXX', well_id = 1234)

def request_entities(**kwargs):
    pass

def build_uris(well_ids = []):
    for well_id in well_ids:
        uri.format(well_id = well_id)


WELLS.session.query(WELLS).with_entities(*WELLS.get_pk_cols()).all()

WELLS.get_ids()

PROD.get_ids()

PROD.get_pk_cols()

dir

