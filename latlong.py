#!/home/nik/github/location/venv/bin/python

#
# Add lat/long information to addresses
#
# CSV input:
# Date,Address,Reason
# 2024/01/01 13:21:00,171 HARTFORD ST,MOTOR VEHICLE STOP SUMMONS REQUEST
#
# onetime input:
# --onetime '171 HARTFORD ST'




# Library to convert addresses
# pip install geopy
from geopy.geocoders import Nominatim


import argparse
import re

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

    # Add in town/state if needed
    if (not re.search(lookfor, addressline)):
        args.debug and print(f'Did not find {lookfor} so added {add} to address')
        addressline += f', {add}'

    getLoc = loc.geocode(addressline)
    return (f'{getLoc.latitude:.6f}',f'{getLoc.longitude:.6f}',f'{getLoc.address}')


#
# Init connection to Geopy
#
loc = Nominatim(user_agent="Geopy Library")

if (args.onetime):
    address = args.onetime
    args.debug and print(f'One time address of >>>{address}<<<')
    (lat,long,normalized) = latlong(address,args.lookfor,args.add,loc)

    # Show information about the address
    print(f'Normalized address = {normalized}')
    print(f'Latitude = {lat}')
    print(f'Longitude = {long}')
