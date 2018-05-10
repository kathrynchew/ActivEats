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

    # >>> f = open("all_recipes_0.csv")
    # >>> lines = f.readlines()
    # >>> lines[0]
    # >>> lines[0].split(",")

    recipe_file = open("../scrapy/recipe_yum/recipe_yum/spiders/all_recipes_0.csv")
    recipe_lines = recipe_file.readlines()

    for line in recipe_lines:
        line = line.split(",")
        total_time = line[0]
        active_time = line[1]
        ingredients = line[2]
        url = line[3]
        preparation = line[4]
        difficulty = line[5]
        recipe_name = line[6]
        inactive_time = line[7]
        special_equipment = line[8]
        prep_time = line[9]
        servings = line[10]
        recipe_author = line[11]
        photo_url = line[12]
        category_tags = line[13]
        cook_time = line[14]

        # Read CSV data file & insert data
        # for row in open("../scrapy/recipe_yum/recipe_yum/spiders/all_recipes_0.csv"):
        #     row = row.rstrip().split(",")


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
    load_recipes()
    set_val_recipe_id()
