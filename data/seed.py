""" Utility file to clean & seed recipe database from scraped data """

from sqlalchemy import func
# from datetime import datetime, datetime
from model import SampleFNRecipe, connect_to_db, db
from server import app


def load_recipes():
    """ Load recipes into SAMPLE database """

    print "Adding SampleFNRecipe"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    SampleFNRecipe.query.delete()

    # Read CSV data file & insert data
    for row in open("../scrapy/recipe_yum/recipe_yum/spiders/all_recipes_0.csv"):
        row = row.rstrip()
        total_time, active_time, ingredients, url, preparation, difficulty, recipe_name, inactive_time, special_equipment, prep_time, servings, recipe_author, photo_url, category_tags, cook_time = row.split(",")

        recipe = SampleFNRecipe(recipe_name=recipe_name,
                                recipe_author=recipe_author,
                                category_tags=category_tags,
                                difficulty=difficulty,
                                servings=servings,
                                special_equipment=special_equipment,
                                ingredients=ingredients,
                                preparation=preparation,
                                total_time=total_time,
                                prep_time=prep_time,
                                cook_time=cook_time,
                                active_time=active_time,
                                inactive_time=inactive_time,
                                photo_url=photo_url,
                                recipe_url=url)

        db.session.add(recipe)

    db.session.commit()


def set_val_recipe_id():
    """Set value for the next recipe_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(SampleFNRecipe.recipe_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('samplerecipes_recipe_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()



################################################################################
# HELPER FUNCTIONS

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_recipe()
    set_val_recipe_id()
