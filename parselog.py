#!/home/nik/github/location/venv/bin/python


#
# Parse Town of Natick police logs PDFs into one CSV of interesting things
#




# pip install PyPDF2
from PyPDF2 import PdfReader 

# address -> lat/long
# https://geocoding.geo.census.gov/geocoder/
# https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
# https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=4600+Silver+Hill+Rd%2C+Washington%2C+DC+20233&benchmark=4&format=json
import requests

import argparse
import re
import sys


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


args = argParser.parse_args()

if (args.debug): 
    print(f"You passed filename(s) >>>{args.input}<<<")


#
# Given an address line, parse out the vague information to focus on the street
# Returns:
# log_location,latitude,longitude,normalized_location
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
        return (None,None,None,None)

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
            return(log_address,
                   f"{data['result']['addressMatches'][0]['coordinates']['y']:.6f}",
                   f"{data['result']['addressMatches'][0]['coordinates']['x']:.6f}",
                   f"{data['result']['addressMatches'][0]['matchedAddress']}"
            )

    print(f">>>>>> WARNING, NO GEO information for {addresswithtown} (parsed from >>{addressline}<<)",file=sys.stderr)
    return (None,None,None,None)


# CSV output header
print(f'Date,Address,Reason,lat,long,Normalized_Address')

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
                reason = f'{match.group(5).strip()}'
                if args.debug: print(line)

            #
            # If we are watching this section, is it an address line?
            # Some address lines have address1 @ address2 so handle those
            #
            if (interesting and ((match := re.search('Location/Address: (.*)', line)) or
                                 (match := re.search('Vicinity of: (.*)', line)))):
                if args.debug: print(line)
                addressline = match.group(1).strip()
                for address in addressline.split('@'):
                    (log_location,lat,long,normalized_location) = extract_location(address)
                    if (log_location):
                        print (f'{date} {time},"{log_location}","{reason}",{lat},{long},"{normalized_location}"')
                        break
            
        if args.debug: print("=================== NEXT PDF PAGE =======================================")
