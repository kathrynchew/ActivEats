from sqlalchemy import func
from model import User, Collection, UserPreference, connect_to_db, db
from server import app
import os


def load_collections():

    print "Adding User Collections"

    user_id = User.query.filter_by(email=os.environ['SAMPLE_EMAIL']).first().user_id

    with open('data/recipe_files/past_meals.csv') as file:

        for line in file:

            line = line.rstrip().split(',')

            col_data = Collection(user_id=user_id,
                                  assigned_date=line[2].lstrip().rstrip(),
                                  set_number=line[3].lstrip().rstrip(),
                                  set_day=line[4].lstrip().rstrip(),
                                  meal_type=line[5].lstrip().rstrip(),
                                  recipe_id=line[6].lstrip().rstrip())

            db.session.add(col_data)

        db.session.commit()


def load_user():
    print "Adding Sample User"

    user_data = User(username=os.environ['SAMPLE_USERNAME'],
                     password=os.environ['SAMPLE_PASSWORD'],
                     email=os.environ['SAMPLE_EMAIL'])

    db.session.add(user_data)
    db.session.commit()


def load_prefs():
    print "Adding Sample User Preference(s)"

    user_id = User.query.filter_by(email=os.environ['SAMPLE_EMAIL']).first().user_id

    user_pref = UserPreference(user_id=user_id,
                               category_id=528)

    db.session.add(user_pref)
    db.session.commit()


def load_sample_user():
    load_user()
    load_prefs()
    load_collections()


################################################################################
if __name__ == "__main__":
    connect_to_db(app)

    load_user()
    load_prefs()
    load_collections()
