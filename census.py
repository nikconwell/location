#!/home/nik/github/location/venv/bin/python

import requests

def get_geocode(address):
    # API endpoint
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

    # Parameters for the request
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }

    # Sending the request
    response = requests.get(url, params=params)

    # Checking if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Example usage
address = "49 ELIOT ST, natick, ma"
geocode_data = get_geocode(address)

if geocode_data:
    print("Geocode Data:", geocode_data)
else:
    print("Failed to retrieve data.")
