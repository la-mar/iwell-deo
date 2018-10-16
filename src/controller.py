
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

# WELLS.session.query(WELLS).filter_by(well_id = wells.dfo[0].well_id).scalar() is not None

# WELLS.session.query(WELLS).with_entities(*pk_cols).all()
# WELLS.session.query(WELLS).filter().all()


# WELLS.session.dirty

# pk_cols = []
# for k, v in WELLS.__table__.c.items():
#     if v.primary_key:
#         pk_cols.append(v)

# wells.dfo[0].exists()

# for x in wells.dfo:
#     print(x.well_id in wells.in_db)

# wells.dfo[0].__dict__


# trans = []
# wells.df['action'] = wells.df.apply(find_action)
for obj in wells.dfo:
    print(inspect(obj).persistent)
    WELLS.session.merge(obj)
    print(inspect(obj).persistent)

WELLS.session.new
WELLS.session.dirty
WELLS.session.commit()
WELLS.session.rollback()


# WELLS.session.is_modified(WELLS)
# x= WELLS.session.dirty.pop()

# x.well_type = 'NONE'
# x.__dict__
# WELLS.session.add(x)
# WELLS.session.identity_map.__dict__
# dir(inspect(obj))
# WELLS.session.query(WELLS).first()
# type(wells.obj)
# type(WELLS.session.query(WELLS.__table__).all())
# type(WELLS.session.query(WELLS.__table__).first())
# WELLS(**wells.in_db[0])
# [x for x in wells.obj]
# type(wells.in_db)
# type(wells.obj[0])
# WELLS.session.query(WELLS).filter.__dir__()
# WELLS.session.query(WELLS).exists()
# result_dict = map(lambda q: q._asdict(), WELLS.session.query(WELLS.__table__))
# result_dict[0]




# WELLS.session.add_all(wells.in_db)
# WELLS.session.add_all(wells.dfo)



# object_state(wells.obj[0]).__getstate__()
# TODO: START HERE -> Get "merge" method from Flowback

#TODO: Merge -> load inserts -> load updates

# Get List of id's
e_ids = [record[0] for record in e_wells]

e_mask = wells.df.well_id.isin(e_ids)

WELLS.session.new
WELLS.session.dirty
WELLS.session.commit()
WELLS.session.rollback()

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


# TODO: load updates

# TODO: load inserts
























# TODO: True up










