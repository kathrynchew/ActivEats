import os
import requests

api_key = os.environ['USDA_KEY']
query_key = '&api_key=' + api_key
start_string = 'https://api.nal.usda.gov/ndb/search/?format=json&q='

query_term = 'cinnamon%20basil'

r = requests.get(start_string + query_term + query_key)
results_json = r.json()
