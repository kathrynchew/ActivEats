import os
import requests
import datetime
from pprint import pprint
from stravalib.client import Client
from stravalib import unithelper

access_token = os.environ['STRAVA_TOKEN']
client_id = os.environ['STRAVA_CLIENT_ID']
client_secret = os.environ['STRAVA_CLIENT_SECRET']
athlete_id = os.environ['STRAVA_ATHLETE_ID']


client = Client()

client.access_token = access_token


def query_athlete():
    return client.get_athlete()


def query_activities():
    iso_now = datetime.datetime.now().isoformat()

    return client.get_activities(before=iso_now, limit=100)

# for activity in activities:
#     print activity.name
