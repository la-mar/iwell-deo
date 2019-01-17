import logging
from src.requestor import *
from src.dbagents import *

from src.settings import LOAD_TO_DB, DEFAULT_START

logger = logging.getLogger(__name__)

# Setup

#! CLASSES in CAPS represent Driftwood_DB tables

#! Classes in CamelCase represent iWell objects

db = iwell_agent()
wells = iwell_api('wells')
prod = iwell_api('production')
meters = iwell_api('meters')
meter_readings = iwell_api('meter_readings')
fields = iwell_api('fields')
fields_by_well = iwell_api('fields_by_well')
field_values = iwell_api('field_values')

tanks = iwell_api('tanks')
tank_readings = iwell_api('tank_readings')
well_tanks = iwell_api('well_tanks')
run_tickets = iwell_api('run_tickets')
well_notes = iwell_api('well_notes')
well_groups = iwell_api('well_groups')
well_group_wells = iwell_api('well_group_wells')

#**
WELLS.session = db.Session()
PROD.session = db.Session()
METERS.session = db.Session()
METER_READINGS.session = db.Session()
FIELDS.session = db.Session()
FIELDS_BY_WELL.session = db.Session()
FIELD_VALUES.session = db.Session()

TANKS.session = db.Session()
TANK_READINGS.session = db.Session()
WELL_TANKS.session = db.Session()
RUN_TICKETS.session = db.Session()
WELL_NOTES.session = db.Session()
WELL_GROUPS.session = db.Session()
WELL_GROUP_WELLS.session = db.Session()





# FIXME: Updating o)


def find_delta(api, table):
    d1 = prod.get_last_success()
    d2 = PROD.get_last_update()[0]
    return d1 if d1 < d2 else d2



def integrate():

    #! Wells

    #** Build URIs
    wells.request_uri(wells.build_uri())

    #** Clean up wells from iWell
    wells.parse_response()


    if LOAD_TO_DB:

        #** Merge records into session
        WELLS.merge_records(wells.df)

        #** Get affected row counts
        WELLS.get_session_state()

        #** Persist changes to database
        WELLS.persist()



    #! Production


    #* Pull
    # Build URIs
    prod.build_uris(WELLS.keyedkeys(), start = DEFAULT_START)

    # Make requests
    prod.request_uris()
    # prod.uris
    # Clean up response
    prod.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        PROD.merge_records(prod.df)

        # Get affected row counts
        PROD.get_session_state()

        # Persist changes to database
        PROD.persist()


    #! Meters

    #* Pull
    # Build URIs
    meters.build_uris(WELLS.keyedkeys())

    # Make requests
    meters.request_uris()

    # Clean up response
    meters.parse_response()

    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        METERS.merge_records(meters.df)

        # Get affected row counts
        METERS.get_session_state()

        # Persist changes to database
        METERS.persist()



    #! Meter Readings


    #* Pull
    # Build URIs
    meter_readings.build_uris(METERS.keyedkeys(),
                )

    # Make requests
    meter_readings.request_uris()

    # Clean up response
    meter_readings.parse_response()

    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        METER_READINGS.merge_records(meter_readings.df)

        # Get affected row counts
        METER_READINGS.get_session_state()

        # Persist changes to database
        METER_READINGS.persist()



    #! Fields

    #* Pull
    # Make requests
    fields.request_uri(fields.build_uri())

    # Clean up response
    fields.parse_response()

    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        FIELDS.merge_records(fields.df)

        # Get affected row counts
        FIELDS.get_session_state()

        # Persist changes to database
        FIELDS.persist()


    #! Fields by Well

    #* Pull
    # Build URIs
    fields_by_well.build_uris(WELLS.keyedkeys(),
                )

    # Make requests
    fields_by_well.request_uris()

    # Clean up response
    fields_by_well.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        FIELDS_BY_WELL.merge_records(fields_by_well.df)

        # Get affected row counts
        FIELDS_BY_WELL.get_session_state()

        # Persist changes to database
        FIELDS_BY_WELL.persist()


    #! Field Values

    #* Pull
    # Build URIs
    field_values.build_uris(FIELDS_BY_WELL.keyedkeys(),
            )

    # Make requests
    field_values.request_uris()

    # Clean up response
    field_values.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        FIELD_VALUES.merge_records(field_values.df)

        # Get affected row counts
        FIELD_VALUES.get_session_state()

        # Persist changes to database
        FIELD_VALUES.persist()


    # field_values.df = field_values.df.fillna(0)


    # FIELD_VALUES.session.rollback()



    #! Tanks

    #* Pull
    # Make requests
    tanks.request_uri(tanks.build_uri())

    # Clean up response
    tanks.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        TANKS.merge_records(tanks.df)

        # Get affected row counts
        TANKS.get_session_state()

        # Persist changes to database
        TANKS.persist()


    #! Tank Readings

    #* Pull
    # Build URIs
    tank_readings.build_uris(TANKS.keyedkeys(),
                )

    # Make requests
    tank_readings.request_uris()

    # Clean up response
    tank_readings.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        TANK_READINGS.merge_records(tank_readings.df)

        # Get affected row counts
        TANK_READINGS.get_session_state()

        # Persist changes to database
        TANK_READINGS.persist()


    #! Well Tanks

    #* Pull
    # Build URIs
    well_tanks.build_uris(WELLS.keyedkeys(),
        )

    # Make requests
    well_tanks.request_uris()

    # Clean up response
    well_tanks.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        WELL_TANKS.merge_records(well_tanks.df)

        # Get affected row counts
        WELL_TANKS.get_session_state()

        # Persist changes to database
        WELL_TANKS.persist()

    # SECTION: Run Tickets

    #* Pull
    # Build URIs
    run_tickets.build_uris(TANK_READINGS.keyedkeys(),
            )

    # Make requests
    run_tickets.request_uris()

    # Clean up response
    run_tickets.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        RUN_TICKETS.merge_records(run_tickets.df)

        # Get affected row counts
        RUN_TICKETS.get_session_state()

        # Persist changes to database
        RUN_TICKETS.persist()


    #! Well Notes

    #* Pull
    # Build URIs
    well_notes.build_uris(WELLS.keyedkeys(),
            )

    # Make requests
    well_notes.request_uris()

    # Clean up response
    well_notes.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        WELL_NOTES.merge_records(well_notes.df)

        # Get affected row counts
        WELL_NOTES.get_session_state()

        # Persist changes to database
        WELL_NOTES.persist()


    #! Well Groups

    #* Pull
    # Make requests
    well_groups.request_uri(well_groups.build_uri())

    # Clean up response
    well_groups.parse_response()
    # Extra steps for this one stupid group
    well_groups.df.created_iwell = well_groups.df.created_iwell.apply(pd.datetime.fromtimestamp)
    well_groups.df.updated_iwell = well_groups.df.updated_iwell.apply(pd.datetime.fromtimestamp)
    well_groups.df.group_latest_production_time  = well_groups.df.group_latest_production_time .apply(pd.datetime.fromtimestamp)


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        WELL_GROUPS.merge_records(well_groups.df)

        # Get affected row counts
        WELL_GROUPS.get_session_state()

        # Persist changes to database
        WELL_GROUPS.persist()



    #! Well Group Wells

    # Build URIs
    well_group_wells.build_uris(WELL_GROUPS.keyedkeys(),
                )

    # Make requests
    well_group_wells.request_uris()

    # Clean up response
    well_group_wells.parse_response()


    if LOAD_TO_DB:

        #* Push
        # Merge records into session
        WELL_GROUP_WELLS.merge_records(well_group_wells.df)

        # Get affected row counts
        WELL_GROUP_WELLS.get_session_state()

        # Persist changes to database
        WELL_GROUP_WELLS.persist()









