#!/home/nik/github/location/venv/bin/python


#
# Parse Town of Natick police logs PDFs into one CSV of interesting things
#

# 1. Read given PDF
# 2. Look for sections which indicate an activity and reason
# 3. Look for location or vicinity in the section for address information.
# 4. Use Census web api to convert address to lat long. Note this is not really the most accurate
#    but it is free.



# pip install PyPDF2
from PyPDF2 import PdfReader 

# address -> lat/long
# https://geocoding.geo.census.gov/geocoder/
# https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
# https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=4600+Silver+Hill+Rd%2C+Washington%2C+DC+20233&benchmark=4&format=json
import requests

import argparse
import re
import os
import sys
import json


#
# Args
#
argParser = argparse.ArgumentParser(prog="parselog.py",
                                    description="Read Town of Natick Police Logs, extracting address information")
                                    
argParser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Debug mode for various things')
argParser.add_argument('--input', dest='input', required=True, nargs='+', help='PDF file(s) to parse / process')
argParser.add_argument('--justdump', dest='justdump', default=False, action='store_true', help="Just dump the entire pdf, no processing")
argParser.add_argument('--lookfor', dest='lookfor', default='natick', help='regex to look for in the address (default natick)')
argParser.add_argument('--add', dest='add', default='natick, ma, 01760', help='Town to add at the end of the address (based on if lookfor is true) (default "natick, ma, 01760")')
argParser.add_argument('--geodata', dest='geodata', default='geodata.json', help='File containing cached geolocation information so we do not repeatedly look things up')
argParser.add_argument('--geofail', dest='geofail', default='geofail.json', help='File containing geolocation failures so we can try to resolve them later with other things')


args = argParser.parse_args()

if (args.debug): 
    print(f"You passed filename(s) >>>{args.input}<<<")



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
# Given an address line, parse out the vague information to focus on the street
# Returns:
# normalized_address,latitude,longitude
#
def extract_location(addressline):
    regexes = [r'(\d+[\w ]+\s+ST)',
               r'(\d+[\w ]+\s+RD)',
               r'(\d+[\w ]+\s+AVE)',
               r'(\d+[\w ]+\s+WAY)',
               r'(\d+[\w ]+\s+CIR)',
               r'(\d+[\w ]+)',             # catch all with no rd, st, ave, etc.
    ]
    log_address=None

    for regex in regexes:
        match = re.search(regex,addressline)
        if (match):
            log_address = match.group(1)
            break
    if (not log_address):
        print(f">>>>>> WARNING, NOT ABLE TO PARSE ADDRESS {addressline}",file=sys.stderr)
        return (None,None,None)

    addresswithtown = log_address
    if (not re.search(args.lookfor,addresswithtown)):
        addresswithtown += f', {args.add}'


    args.debug and print(f'>>>>>> {addressline} ==PARSED==> Querying {addresswithtown} ')
    
    response = requests.get("https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
                            params = {
                                "address": addresswithtown,
                                "benchmark": "Public_AR_Current",
                                "format": "json"
                                }
                            )
    if response.status_code == 200:
        data = response.json()
        if len(data['result']['addressMatches']):
            return(f"{data['result']['addressMatches'][0]['matchedAddress']}",
                   f"{data['result']['addressMatches'][0]['coordinates']['y']:.6f}",
                   f"{data['result']['addressMatches'][0]['coordinates']['x']:.6f}",
            )

    print(f">>>>>> WARNING, NO GEO information for {addresswithtown} (parsed from >>{addressline}<<)",file=sys.stderr)
    return (None,None,None)




#
# Given a reason from the logs, focus down on common reasons
#
def extract_reason(log_reason):
    normalized_reason=log_reason
    # More general patterns at the end
    patterns = [r'\s*log\s+entry\s*',
                r'\s*services\s+\S+',
                r'\s*report to be filed',
                r'\s*citation/\s+warning\s+issued',
                r'\s*summons\s+request\s*',
                r'\s*gone\s+on\s+arrival\s*',
                r'\s+P\s+-\s*',
                r'\s*F\s+-\s*',
                r'^\s+',
                r'\s+$'
                ]
    for pattern in patterns: 
        normalized_reason=re.sub(pattern,'',normalized_reason,flags=re.IGNORECASE)
    return(normalized_reason)





#
#
# Main Code
#
#

# CSV output header
print(f'Date,Log_Address,Log_Reason,Normalized_Reason,lat,long,Normalized_Address')

#
# Iterate through the given PDFs
#
    
for filename in args.input:
    if args.debug: print(f'>>>>>> Processing {filename}')
    reader = PdfReader(filename)
    if args.debug: print(f'>>>>>> PDF has {len(reader.pages)} pages')

    interesting = False         # Will set to True when we want to focus on an interesting "paragraph" of the text. Could span 2 pages...
    date = None
    time = None


    #
    # Iterate pages in the PDF
    #
    for page in reader.pages:
        args.debug and print(">>>>>> Processing page")
        text = page.extract_text()

        #
        # Iterate through each line of this page.
        #
        for line in text.split('\n'):
            # Just dumping entire file to text? Print and shortcut here.
            if (args.justdump):
                print(line)
                continue
            #
            # Line indicating what date we are working on?
            #                                          MM /  DD / YYYY
            #                                           1     2    3
            if (match := re.search(r'^\s*For Date:\s*(\d+)/(\d+)/(\d+)', line)):
                date = f'{match.group(3)}/{match.group(1)}/{match.group(2)}'

            # Are we in a new section???
            #                          24-22            2331        MOTOR VEHICLE STOP Citation/ Warning Issued
            #                          YY-COUNT         HHMM        REASON
            #                          1     2         3    4       5
            if (match := re.search(r'^(\d+)-(\d+)\s+(\d\d)(\d\d)\s+(.*)', line)):
                interesting = True
                time = f'{match.group(3)}:{match.group(4)}:00'
                log_reason = f'{match.group(5).strip()}'
                if args.debug: print(line)

            #
            # If we are watching this section, is it an address line?
            # Some address lines have address1 @ address2 so handle those
            #
            if (interesting and ((match := re.search('Location/Address: (.*)', line)) or
                                 (match := re.search('Vicinity of: (.*)', line)))):
                if args.debug: print(line)
                addressline = match.group(1).strip()
                for log_address in addressline.split('@'):
                    normalized_address = None
                    if (log_address in geofail):
                        if args.debug: print(f">>>>>> No GEO information for address (as per {geofail}) so skipping {log_address}",file=sys.stderr)
                        continue
                    if (log_address in geodata):
                        lat = geodata[log_address]['lat']
                        long = geodata[log_address]['long']
                        normalized_address = geodata[log_address]['normalized_address']
                    else:
                        (normalized_address,lat,long) = extract_location(log_address)
                        if (normalized_address):
                            geodata[log_address] = {'coder': 'census', 'normalized_address': normalized_address, 'lat': lat, 'long': long}
                        else:
                            geofail[log_address] = {'coder': 'census'}
                    if (normalized_address):
                        normalized_reason = extract_reason(log_reason)
                        print (f'{date} {time},"{log_address}","{log_reason}","{normalized_reason}",{lat},{long},"{normalized_address}"')
                        break
            
        if args.debug: print("=================== NEXT PDF PAGE =======================================")


# Finally at the end, save off our geodata

with open(args.geodata, 'w') as json_file:
    json.dump(geodata, json_file, indent=4)
if args.debug: print(f'geodata saved to {args.geodata}')
with open(args.geofail, 'w') as json_file:
    json.dump(geofail, json_file, indent=4)
if args.debug: print(f'geofail saved to {args.geofail}')
