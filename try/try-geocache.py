#!/home/nik/github/location/venv/bin/python

#
# Experiment with saving cached geodata.
#

import json

# geodata = {'1 Main Street': {'coder': 'census', 'lat': -1.234567, 'long': 99.59849857},
#            '1 Oak Street': {'coder': 'census', 'lat': -1.987654321, 'long': 99.123456789, 'normalized': '1 Oak Street, Natick, MA'},
#            }


# with open('geodata.json', 'w') as json_file:
#     json.dump(geodata, json_file, indent=4)

# print("Restructured dictionary saved to geodata.json")


with open('geodata.json', 'r') as json_file:
    geodata = json.load(json_file)

# Print the loaded dictionary
print(geodata)

print(geodata['1 Oak Street'])
