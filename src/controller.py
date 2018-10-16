
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

#? session handling could be wonky here
WELLS.session = db.Session()

# WELLS.session.query(WELLS.__table__).all()


#? Transport



e_wells = WELLS.get_existing_records()

#** Get wells from iWell
wells.request_entity()

#** Clean up wells from iWell
wells.parse_response()

#** Give existing ids to iWell object
# wells.in_db = WELLS.get_existing_records()

#** flag inserts and updates

wells.dfo = []
for idx, row in wells.df.iterrows():
    # wells.dfo.append(WELLS(**row.to_dict()))
    wells.dfo.append(WELLS.session.merge(WELLS(**row.to_dict())))

WELLS.session.add_all(wells.dfo)


WELLS.session.new
WELLS.session.dirty
WELLS.session.identity_map.__dict__['_dict'].values()



WELLS.session.commit()
WELLS.session.rollback()



# object_state(wells.obj[0]).__getstate__()
# TODO: START HERE -> Get "merge" method from Flowback

#TODO: Merge -> load inserts -> load updates

# Get List of id's
# e_ids = [record[0] for record in e_wells]

# e_mask = wells.df.well_id.isin(e_ids)

# WELLS.session.new
# WELLS.session.dirty
# WELLS.session.commit()
# WELLS.session.rollback()

# # Bool mask: Does a prod record for this api and datetime exist in the database?
# emask = prod_df.prod_datetime.isin(edt)
# # print(emask)
# # pprint(prod_df.head())
# # Remove duplicates
# prod_df = prod_df \
#         .sort_values(pks, axis = 0, ascending = False) \
#         .drop_duplicates(keep ='first', subset = pks)

# # Rows with a PK already in the database
# potential_updates = prod_df[emask]

# # Rows that dont have an existing PK in the database
# inserts = prod_df[~emask]
# # print(inserts)
# updates = []
# for idx, row in potential_updates.iterrows():
#     f = self.Flowback(**row.to_dict())
#     if f in edt:
#         updates.append(f)


# TODO: load updates

# TODO: load inserts
























# TODO: True up










