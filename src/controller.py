
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

db = iwell_agent()
wells = iwell_api('wells')

#? session handling could be wonky here
WELLS.session = db.Session()




#? Transport
existing_wells = WELLS.get_existing()

wells.request_entity()


# TODO: START HERE -> Get "merge" method from Flowback

#TODO: Merge -> load inserts -> load updates



























# TODO: True up










