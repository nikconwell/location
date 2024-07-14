#!/home/nik/github/location/venv/bin/python

#
# Add lat/long information to addresses
#
# CSV input:
# --input {filename}
# Date,Address,Reason
# 2024/01/01 13:21:00,171 HARTFORD ST,MOTOR VEHICLE STOP SUMMONS REQUEST
#
# onetime input:
# --onetime '171 HARTFORD ST'


# address -> lat/long
from geopy.geocoders import Nominatim

# csv reading
import pandas as pd


import argparse
import re
import sys

#
# Args
#
argParser = argparse.ArgumentParser(prog="latlong.py",
                                    description="Convert street address to latitude/longitude.")
                                    
argParser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Debug mode for various things')
argParser.add_argument('--input', dest='input', nargs='+', help='CSV file(s) to parse / process')
argParser.add_argument('--onetime', dest='onetime', default=False, help='Single address for conversion')
argParser.add_argument('--lookfor', dest='lookfor', default='natick', help='regex to look for in the address')
argParser.add_argument('--add', dest='add', default='natick, ma', help='Town to add at the end of the address (based on if lookfor is true)')
argParser.add_argument('--javascript', dest='javascript', default=False, action='store_true', help='Output latitude and longitude in javascript format suitable for Google Maps API')

args = argParser.parse_args()


#
# Look up lat/long for the address
# Returns:
# (lat,long,normalized_address)
#
def latlong(addressline,lookfor,add,loc):
    lat=None
    long=None

    args.debug and print(f'In latlong() lookfor={lookfor} add={add} loc={loc}')
    # Add in town/state if needed
    if (not re.search(lookfor, addressline)):
        args.debug and print(f'Did not find {lookfor} so added {add} to address')
        addressline += f', {add}'

    args.debug and print(f'About to loc.geocode(str({addressline}))')
    getLoc = loc.geocode(addressline)
    if getLoc:
        return (f'{getLoc.latitude:.6f}',f'{getLoc.longitude:.6f}',f'{getLoc.address}')
    else:
        return (None,None,None)

#
# Wrapper for above latlong for when called by the DataFrame.apply() function
#
def apply_latlong(entry,lookfor,add,loc):
    args.debug and print(f'>>>>>> in apply_latlong(): entry={entry}')
    (lat,long,normalized) = latlong(entry.Address,lookfor,add,loc)
    if args.debug: print(f'latlong() returned: ({lat},{long},{normalized})')
    entry['lat'] = lat
    entry['long'] = long
    entry['normalized'] = normalized
    return entry


#
# Init connection to Geopy
#
loc = Nominatim(user_agent="Geopy Library")


#
# --onetime invocation
# Just call the latlong function with the info.
#

if (args.onetime):
    address = args.onetime
    args.debug and print(f'One time address of >>>{address}<<<')
    (lat,long,normalized) = latlong(address,args.lookfor,args.add,loc)

    # Show information about the address
    print(f'Normalized address = {normalized}')
    print(f'Latitude = {lat}')
    print(f'Longitude = {long}')

    exit

#
# --input {filename} invocation
# Read into pandas DataFrame and use the DataFrame.apply() method to iterate each row and call
# our apply_latlong() function for each row
#

    
if (args.input):
    for filename in args.input:
        if args.debug: print(f'>>>>>> Processing {filename}')
        if filename == '-':
            filename = sys.stdin
        traffic_stop_info = pd.read_csv(filename)
        if args.debug: print(f'>>>>>> Created {traffic_stop_info}')

        # Now use apply() to chow through the DataFrame calling apply_latlong() on each row
        new_traffic_stop_info = traffic_stop_info.apply(apply_latlong,axis=1,by_row='compat',args=(args.lookfor,args.add,loc))

        if args.debug: print(f'{new_traffic_stop_info}')

        new_traffic_stop_info.to_csv(sys.stdout,index=False)
