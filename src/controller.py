
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

# #** Get wells from iWell
# wells.request_entity(delta= (datetime.now() - timedelta(days = 1)))

# wells.uris

# wells.build_uris(ids = {})#, delta = wells.get_last_success())

# wells.url

#** Get wells from iWell
wells.request_uri(wells.build_uri())

#** Clean up wells from iWell
wells.parse_response()

#** Merge records into session
WELLS.merge_records(wells.df)

#** Get affected row counts
WELLS.get_session_state()

#** Persist changes to database
WELLS.persist()



#** Get wells from iWell

#** Get wells from iWell
prod.build_uris(WELLS.keyedkeys(), delta = prod.get_last_success())

prod.request_uris()

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

def build_uri(well_id = None, group_id = None, tank_id = None
            , run_ticket_id = None, meter_id = None):
     """Wrapper to build a uri from a set of identifiers
    
    Arguments:
        well_id {str} (optional) --
        group_id {str} (optional) --
        tank_id {str} (optional) --
        run_ticket_id {str} (optional) --
        meter_id {str} (optional) --
    
    Returns:
        {str} -- uri endpoint
    """
    return uri.format(well_id = well_id
                    , group_id = group_id
                    , tank_id = tank_id
                    , run_ticket_id = run_ticket_id
                    , meter_id = meter_id)

def build_uris(ids: list):
    """Wrapper to build multiple uris from a list of ids
    
    Arguments:
        ids {list} -- list of dicts of identifiers
    
    Returns:
        {list} -- list of populated uri endpoints
    """

    return [build_uri(**x) for x in ids]

wells.df['well_id'].to_dict('records')

wells.keys()

wells.df[[wells.aliases['id']]].to_dict('records')

query = WELLS.session.query(WELLS).with_entities(*WELLS.get_pk_cols())
list(pd.read_sql(query.statement, query.session.bind).squeeze().values)

# ids = [{'well_id' : x} for x in wells.keys()]

# x = build_uris(ids)
# x


wells.reload_properties()

wells.endpoint

WELLS.session.query(WELLS).with_entities(*WELLS.get_pk_cols()).all()

WELLS.get_ids()

PROD.get_ids()

PROD.get_pk_cols()


# [x['path'] for x in _properties['endpoints'].values()]

for k,v in _properties['endpoints'].items():
    print(k)

for k,v in _properties['endpoints'].items():
    print(v['path'])

print(', '.join(['{}={!r}'.format(k, v) for k, v in x.items()]))
