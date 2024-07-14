#!/home/nik/github/location/venv/bin/python


#
# Parse Town of Natick police logs PDFs into one line of interesting things
#




# pip install PyPDF2
from PyPDF2 import PdfReader 

import argparse
import re


#
# Args
#
argParser = argparse.ArgumentParser(prog="parselog.py",
                                    description="Read Town of Natick Police Logs, extracting address information of any MOTOR VEHICLE STOP.")
                                    
argParser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Debug mode for various things')
argParser.add_argument('--input', dest='input', required=True, nargs='+', help='PDF file(s) to parse / process')
argParser.add_argument('--justdump', dest='justdump', default=False, action='store_true', help="Just dump the entire pdf, no processing")


args = argParser.parse_args()

if (args.debug): 
    print(f"You passed filename(s) >>>{args.input}<<<")


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
    

# CSV output header
print(f'Date,Address,Reason')

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
        args.debug and print("Processing page")
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
                # Do we have an interesting REASON for motor vehicle stop?
                if re.search('MOTOR VEHICLE STOP',match.group(5)):
                    interesting = True
                    time = f'{match.group(3)}:{match.group(4)}:00'
                    reason = f'{match.group(5)}'
                    if args.debug: print(line)
                else:
                    interesting = False

            #
            # If we are watching this section, is it an address line?
            #
            if (interesting and ((match := re.search('Location/Address: (.*)', line)) or
                                 (match := re.search('Vicinity of: (.*)', line)))):
                if args.debug: print(line)
                if (location := extract_location(match.group(1))):
                    print (f'{date} {time},{location},{reason}')
                    continue
            
        if args.debug: print("=================== NEXT PDF PAGE =======================================")
