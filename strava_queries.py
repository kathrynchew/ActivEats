import os
import datetime
from stravalib.client import Client
from stravalib import unithelper
from isoweek import Week

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

    return results


def act_by_num(num):
    """ Queries stravalib client object for a single activity by activity id.

    Returns full/detailed activity object """

    return client.get_activity(num)


def process_calories(cals_info):
    """ Iterates over a list of weeks to be included (current week and three
        prior weeks in reverse chronological order), matches week numbers
        against keys in dictionary of aggregated calorie totals (keys: week #s,
        values: calorie totals), then appends the respective week numbers and
        calorie totals as a tuple into a list.

        Returns list to get_calories() function to be returned from that
        function."""
    cals_by_week, included_weeks = cals_info
    final_cals_list = []

    for week in included_weeks:
        if week in cals_by_week:
            final_cals_list.append((week, cals_by_week[week]))
        else:
            final_cals_list.append((week, 0))

    return final_cals_list


def get_calories():
    """ Runs all functions needed to query calories from authenticated user's
    last 100 activities, filter for activities occurring in the current week and
    three prior weeks, aggregate recorded calorie expenditures into per-week
    totals, and return this data in the format of a list containing tuples of
    week number (str), total calories (numeric) in reverse chronological order.

    If no calories were recorded in a given week, a zero will be returned in
    the calorie slot of the respective tuple.

    Example: [(24, 200), (23, 582.3), (22, 1502.8), (21, 0)]"""

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

    for key, value in acts_by_week.items():
        for act_id in value:
            act_cals = act_by_num(act_id)

            if key in cals_by_week:
                cals_by_week[key] += act_cals.calories
            else:
                cals_by_week[key] = act_cals.calories

    return process_calories([cals_by_week, included_weeks])
