from sqlalchemy import func
from model import User, Collection, connect_to_db, db
from server import app


def load_collections():

    print "Adding User Collections"

    with open('data/recipe_files/past_meals.csv') as file:
        for line in file:
            # print line
            # user_col_id, user_id, assigned_date, set_number, set_day, meal_type, recipe_id = line.rstrip().split(',')
            # print user_col_id
            # print set_number
            # print meal_type

            line = line.rstrip().split(',')
            print line

            # print line[0].lstrip().rstrip()
            # print line[5].lstrip().rstrip()

            col_data = Collection(user_id=line[1].lstrip().rstrip(),
                                  assigned_date=line[2].lstrip().rstrip(),
                                  set_number=line[3].lstrip().rstrip(),
                                  set_day=line[4].lstrip().rstrip(),
                                  meal_type=line[5].lstrip().rstrip(),
                                  recipe_id=line[6].lstrip().rstrip())

            db.session.add(col_data)

        db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    load_collections()
