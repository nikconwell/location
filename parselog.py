#!/home/nik/github/location/venv/bin/python



# pip install PyPDF2
from PyPDF2 import PdfReader 

import argparse
import re


#
# Parse the vague address information to get a more exact address
#
def extract_location(addressline):
    regexes = ['(\d+[\w ]+\s+ST)',
               '(\d+[\w ]+\s+RD)',
               '(\d+[\w ]+\s+AVE)',
               '(\d+[\w ]+)',             # catch all with no rd, st, ave, etc.
    ]
    parsed=None
    for regex in regexes:
        match = re.search(regex,addressline)
        if (match):
            parsed = match.group(1)
            break
    if (parsed):
        print(f'parsed = {parsed}')
    else:
        print("ERROR, NOT ABLE TO PARSE ADDRESS")
    




#
# Args
#
argParser = argparse.ArgumentParser(prog="parselog.py",
                                    description="Read Town of Natick Police Logs.")
                                    
argParser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Debug mode for various things')
argParser.add_argument('--input', dest='input', required=True, help='PDF file to parse / process')
argParser.add_argument('--justdump', dest='justdump', default=False, action='store_true', help="Just dump the entire pdf, no processing")

args = argParser.parse_args()

print(f"You passed a filename >>>{args.input}<<<")

reader = PdfReader(args.input)
print(f"PDF has {len(reader.pages)} pages")


interesting = False         # Will set to True when we want to focus on an interesting "paragraph" of the text. Could span 2 pages...


#
# Iterate pages in the PDF
#
for page in reader.pages:
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
        # Are we in a new section???
        # 24-22           2331 MOTOR VEHICLE STOP Citation/ Warning Issued
        # YY-DD           HHMM REASON
        match = re.search('^(\d+)-(\d+)\s+(\d+)\s+(.*)', line)
        if (match):
            # Do we have an interesting section for motor vehicle stop?
            if re.search('MOTOR VEHICLE STOP',match.group(4)):
                interesting = True
                print(line)
            else:
                interesting = False

        if (interesting):
            match = re.search('Location/Address: (.*)', line)
            if (match):
                print(line)
                extract_location(match.group(1))
                continue
            match = re.search('Vicinity of: (.*)', line)
            if (match):
                print(line)
                extract_location(match.group(1))
                continue
            
    print("==========================================================")
    
