from __future__ import print_function
from populators.companies import get_company_details
from populators.external.sectors import get_sector_and_industry
from populators.sectors import get_sectors_and_industries
from populators.indicators import get_ratio_data

import json

print('Loading function')


def sector_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    host = event['HOST']
    user = event['USER']
    password = event['PASSWORD']

    get_sectors_and_industries("20", host, user, password)

    return True  # Echo back the first key value
    #raise Exception('Something went wrong')

