from pprint import pprint
import googlemaps



API_KEY = 'AIzaSyBSkxPvw0KCszCH3SwOynTdRqGyfIB_ORc'

# create google map client
map_client = googlemaps.Client(API_KEY)


library_of_congress_address = '101 Independence Ave SE, Washington, DC 20540'
response = map_client.geocode(library_of_congress_address)
pprint(response)
pprint(response[0]['geometry'])