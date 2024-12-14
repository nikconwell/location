#!/home/nik/github/location/venv/bin/python


#
# Take the geodata and make it more accurate by looking up 
# addresses that we only got with the free census lookups which are not accurate.
# Geodata from other APIs are more accurate, but are rate limited so makes processing police logs much
# longer. So we initially use census data but can later refresh with more accurate geodata.
# 

# See also:
# https://github.com/mediagis/nominatim-docker/tree/master/4.5             Docker image for providing GIS data
# https://download.geofabrik.de/north-america/us/massachusetts.html        Massachusetts GIS data download. US can be downlaoded, but is 10G so would take forever to download...


# 1. Read geodata and geofail
# 2. Identify which ones were done based on census data
# 3. Look up the location
# 4. Update geodata and geofail


# address -> lat/long
# https://geocoding.geo.census.gov/geocoder/
# https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
# https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=4600+Silver+Hill+Rd%2C+Washington%2C+DC+20233&benchmark=4&format=json
import requests

# address -> lat/long
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

import argparse
import re
import os
import sys
import json
from time import sleep
from random import randint


#
# Args
#
argParser = argparse.ArgumentParser(prog="refine-geodata.py",
                                    description="Update the geodata.json files with more accurate locations")
                                    
argParser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Debug mode for various things')
argParser.add_argument('--geodata', dest='geodata', default='geodata.json', help='File containing cached geolocation information so we do not repeatedly look things up')
argParser.add_argument('--geofail', dest='geofail', default='geofail.json', help='File containing geolocation failures so we can try to resolve them later with other things')
argParser.add_argument('--add', dest='add', default='natick, ma, 01760', help='Town to add at the end of the address (based on if lookfor is true) (default "natick, ma, 01760")')
argParser.add_argument('--lookfor', dest='lookfor', default='natick', help='regex to look for in the address')


args = argParser.parse_args()




#
# Look up lat/long for the address
# Returns:
# (lat,long,normalized_address)
#
def latlong(addressline: str, lookfor: str, add: str, loc: Nominatim) -> tuple[str,str,str]:
    lat=None
    long=None

    args.debug and print(f'In latlong() lookfor={lookfor} add={add}')
   
    orig_addressline = addressline

    # Remove [ID] crud from beginning of the address.
    addressline = re.sub(r'\s*\[.*\]\s*', '', addressline)

    # If a dash in there, use the last part of the address, after the -
    addressline = re.sub(r'^.*-\s+([^-]+$)', r'\1', addressline)

    # If has apt#, remove that
    addressline = re.sub(r'\s*apt\..*$', '',addressline, flags=re.IGNORECASE)

    # If ends in EXT, remove that bit
    addressline = re.sub(r'\s*ext.*$', '', addressline, flags=re.IGNORECASE)
   
    # Add in town/state if needed
    if (not re.search(lookfor, addressline)):
        args.debug and print(f'Did not find {lookfor} so added {add} to address')
        addressline += f', {add}'

   
    args.debug and print(f'After address cleanup: {addressline}')

    # args.debug and print(f'Doing random sleep between 1 and 20 seconds...')
    # sleep(randint(1*100,20*100)/100)
    
    args.debug and print(f'About to loc.geocode(str({addressline}))')

    getLoc = loc.geocode(addressline)
    if getLoc:
        args.debug and print(f'lat: {getLoc.latitude}, long: {getLoc.longitude}, normalized_address: {getLoc.address}')
        return (f'{getLoc.latitude:.6f}',f'{getLoc.longitude:.6f}',f'{getLoc.address}')
    else:
        print(f'Could not find address {addressline} (originally {orig_addressline})')
        return (None,None,None)


#
# Write out our geodata and geofail files
#

def save_geodata(geodata_file: str, geofail_file: str):
    with open(geodata_file, 'w') as json_file:
        json.dump(geodata, json_file, indent=4)
    if args.debug: print(f'geodata saved to {geodata_file}')
    with open(geofail_file, 'w') as json_file:
        json.dump(geofail, json_file, indent=4)
    if args.debug: print(f'geofail saved to {args.geofail}')




#
#
# Main Code
#
#


# Load in our cache of geodata.
geodata = {}
if (os.path.exists(args.geodata)):
    with open(args.geodata, 'r') as json_file:
        geodata = json.load(json_file)
geofail = {}
if (os.path.exists(args.geofail)):
    with open(args.geofail, 'r') as json_file:
        geofail = json.load(json_file)




#
# Init connection to Geopy
#
our_user_agent = 'user_me_{}'.format(randint(10000,99999))
loc = Nominatim(user_agent=our_user_agent, domain='windows10.splunge', scheme='http')

#
# Iterate the geodata
#
for entry in geodata:
    if (geodata[entry]['coder'] == 'nominatim'): continue
    (new_lat, new_long, normalized_address) = latlong(entry,args.lookfor,args.add,loc)
    if (new_lat):
        geodata[entry]['coder'] = 'nominatim'
        geodata[entry]['lat'] = new_lat
        geodata[entry]['long'] = new_long
        geodata[entry]['normalized_address'] = normalized_address
        if entry in geofail:
            del geofail[entry]

    save_geodata(args.geodata, args.geofail)

save_geodata(args.geodata, args.geofail)
