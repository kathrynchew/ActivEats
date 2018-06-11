import os
import requests
import datetime
from pprint import pprint
from stravalib.client import Client
from stravalib import unithelper
from isoweek import Week
# from flask import jsonify

access_token = os.environ['STRAVA_TOKEN']
client_id = os.environ['STRAVA_CLIENT_ID']
client_secret = os.environ['STRAVA_CLIENT_SECRET']
athlete_id = os.environ['STRAVA_ATHLETE_ID']


client = Client()

client.access_token = access_token


def query_athlete():
    """ Returns profile information for authenticated athlete as an athlete object """
    return client.get_athlete()


def query_activities():
    """ Returns stream of activies for authenticated athlete. Activities in stream
    are summary versions of activity objects; they do not have all fields (must
    query each individually using act_by_num(activity_id) in order to get the 
    full detail level) """

    iso_now = datetime.datetime.now().isoformat()

    results = client.get_activities(before=iso_now, limit=100)

    # return jsonify(results)
    return results


def act_by_num(num):
    """ Queries stravalib client object for a single activity by activity id.

    Returns full/detailed activity object """

    return client.get_activity(num)


def get_calories():

    this_week = Week.thisweek().week
    included_weeks = [str(this_week), str(this_week - 1), str(this_week - 2),
                      str(this_week - 3)]
    activities = query_activities()
    acts_by_week = {}
    cals_by_week = {}

    for act in activities:
        iter_date = act.start_date
        iter_week = iter_date.strftime("%W")
        if iter_week in included_weeks:
            if iter_week in acts_by_week:
                acts_by_week[iter_week].append(act.id)
            else:
                acts_by_week[iter_week] = [act.id]

    print acts_by_week

    for key, value in acts_by_week.items():
        for act_id in value:
            act_cals = act_by_num(act_id)

            if key in cals_by_week:
                cals_by_week[key] += act_cals.calories
            else:
                cals_by_week[key] = act_cals.calories

    return cals_by_week
