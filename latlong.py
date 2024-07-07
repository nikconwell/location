#!/home/nik/github/location/venv/bin/python

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
argParser.add_argument('--javascript', dest='javascript', default=False, action='store_true', help='Output latitude and longitude in javascript format suitable for Google Maps API')
argParser.add_argument('address')

args = argParser.parse_args()

address = args.address
if (args.debug):
    print(f"You entered an address off >>>{address}<<<")

# Add in town/state if needed
if (not re.search('natick', address)):
    address+= ", natick, ma"
    if (args.debug):
        print(f"(Added in town) >>>{address}<<<")

loc = Nominatim(user_agent="Geopy Library")

# Convert address entered
getLoc = loc.geocode(address)

# Show information about the address
print(f"Normalized address = {getLoc.address}")
print(f"Latitude = {getLoc.latitude:.6f}")
print(f"Longitude = {getLoc.longitude:.6f}")
if (args.javascript):
    print(f'{{ lat: {getLoc.latitude:.6f}, lng: {getLoc.longitude:.6f} }}')
