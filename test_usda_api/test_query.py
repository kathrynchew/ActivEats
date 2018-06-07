import os
import requests
import re
from pprint import pprint

api_key = os.environ['USDA_KEY']


def query_by_term(search_term):
    """ Query the USDA Nutrition Data API by searching for a term or phrase """
    search_term = re.sub(r"[^\w\s]", '', search_term)  # Remove all non-digit/letter characters
    search_term = re.sub(r"\s+", '%20', search_term)  # Replace spaces with url-friendly '%20'

    search_string = 'https://api.nal.usda.gov/ndb/search/?format=json&q={}&api_key={}'.format(search_term, api_key)
    results = requests.get(search_string)

    return results.json()


def query_by_number(food_num):
    """ Query the USDA Nutrition Data API by Nutritional Database Number (ndbno) """
    search_number = 'https://api.nal.usda.gov/ndb/reports/?ndbno={}&type=b&format=json&api_key={}'.format(food_num, api_key)

    results = requests.get(search_number)

    return results.json()
