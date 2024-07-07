#!/home/nik/github/location/venv/bin/python



# pip install PyPDF2
from PyPDF2 import PdfReader 

import argparse
import re


#
# Given an address line, parse out the vague information to focus on the street
# Returns:
# The street line as string
#
def extract_location(addressline):
    regexes = [r'(\d+[\w ]+\s+ST)',
               r'(\d+[\w ]+\s+RD)',
               r'(\d+[\w ]+\s+AVE)',
               r'(\d+[\w ]+)',             # catch all with no rd, st, ave, etc.
    ]
    parsed=None
    for regex in regexes:
        match = re.search(regex,addressline)
        if (match):
            parsed = match.group(1)
            break
    if (parsed):
        if args.debug: print(f'parsed = {parsed}')
        return parsed
    else:
        print(f"WARNING, NOT ABLE TO PARSE ADDRESS {addressline}")
        return None
    


#
# Args
#
argParser = argparse.ArgumentParser(prog="parselog.py",
                                    description="Read Town of Natick Police Logs, extracting address information of any MOTOR VEHICLE STOP.")
                                    
argParser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Debug mode for various things')
argParser.add_argument('--input', dest='input', required=True, help='PDF file to parse / process')
argParser.add_argument('--justdump', dest='justdump', default=False, action='store_true', help="Just dump the entire pdf, no processing")

args = argParser.parse_args()

if (args.debug): 
    print(f"You passed a filename >>>{args.input}<<<")

reader = PdfReader(args.input)
if args.debug:
    print(f"PDF has {len(reader.pages)} pages")


interesting = False         # Will set to True when we want to focus on an interesting "paragraph" of the text. Could span 2 pages...
date = None
time = None
#
# Iterate pages in the PDF
#
for page in reader.pages:
    if args.debug:
        print("Processing page")
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
        #                                   MM/DD/YYYY
        if (match := re.search(r'^\s*For Date:\s*(\d+/\d+/\d+)', line)):
            date = match.group(1)

        # Are we in a new section???
        # 24-22           2331 MOTOR VEHICLE STOP Citation/ Warning Issued
        # YY-COUNT        HHMM REASON
        if (match := re.search(r'^(\d+)-(\d+)\s+(\d+)\s+(.*)', line)):
            # Do we have an interesting REASON for motor vehicle stop?
            if re.search('MOTOR VEHICLE STOP',match.group(4)):
                interesting = True
                time = match.group(3)
                if args.debug:
                    print(line)
            else:
                interesting = False

        if (interesting):
            if ((match := re.search('Location/Address: (.*)', line)) or
                 (match := re.search('Vicinity of: (.*)', line))):
                if args.debug: print(line)
                if (location := extract_location(match.group(1))):
                    print (f'{date} {time} {location}')
                continue
            
    if args.debug: print("=================== NEXT PAGE =======================================")
    
