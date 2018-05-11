""" Utility file to clean & seed recipe database from scraped data """

from sqlalchemy import func
from model import SampleFNRecipe, connect_to_db, db
from server import app
import json


def load_recipes():
    """ Load recipes into SAMPLE database """

    print "Adding SampleFNRecipe"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    SampleFNRecipe.query.delete()


   # Open JSON file & parse lines
    with open("../scrapy/recipe_yum/recipe_yum/spiders/all_recipes_jsontest.json") as file:
        recipe_lines = json.load(file)

    for line in recipe_lines:
        url = line['url']
        difficulty = line['difficulty']
        recipe_name = line['recipe_name']
        servings = line['servings']
        recipe_author = line['recipe_author']
        photo_url = line['photo_url']


        ########################################################################
        # CATEGORY TAGS: Populate value as an array

        category_tags = line['category_tags']

        ########################################################################
        # INGREDIENTS: Populate value as an array

        ingredients = line['ingredients']

        ########################################################################
        # SPECIAL EQUIPMENT: Populate with null if null; clean formatting where
        # not null

        if len(line['special_equipment']) == 0:
            special_equipment = None
        else:
            for i in range(len(line['special_equipment'])):
                s = line['special_equipment'][i].lstrip()
                prefix = s[:19]
                if prefix == "Special equipment: ":
                    line['special_equipment'][i] = s[19:].rstrip()
            special_equipment = line['special_equipment']


        ########################################################################
        # PREP INSTRUCTIONS: Clean formatting & add cleaned list of <p> contents

        stripped_prep = []
        for p in line['preparation']:
            stripped_prep.append(p.lstrip().rstrip())
        preparation = stripped_prep


        ########################################################################
        # ALL RECIPE TIMES: Populate with null if null; if not null, typecast
        # into sql interval type

        times = {
            'hr': 'hours',
            'min': 'minutes'
        }

        # TOTAL TIME
        if line['total_time'] == 'N/A':
            total_time = None
        else:
            total_time = ""
            time = line['total_time'].split()
            for t in time:
                if t.isnumeric():
                    total_time = total_time + t
                else:
                    total_time = total_time + " {} ".format(times[t])

        # COOK TIME
        if line['cook_time'] == 'N/A':
            cook_time = None
        else:
            cook_time = ""
            time = line['cook_time'].split()
            for t in time:
                if t.isnumeric():
                    cook_time = cook_time + t
                else:
                    cook_time = cook_time + " {} ".format(times[t])

        # PREP TIME
        if line['prep_time'] == 'N/A':
            prep_time = None
        else:
            prep_time = ""
            time = line['prep_time'].split()
            for t in time:
                if t.isnumeric():
                    prep_time = prep_time + t
                else:
                    prep_time = prep_time + " {} ".format(times[t])

        # ACTIVE TIME
        if line['active_time'] == 'N/A':
            active_time = None
        else:
            active_time = ""
            time = line['active_time'].split()
            for t in time:
                if t.isnumeric():
                    active_time = active_time + t
                else:
                    active_time = active_time + " {} ".format(times[t])

        # INACTIVE TIME
        if line['inactive_time'] == 'N/A':
            inactive_time = None
        else:
            inactive_time = ""
            time = line['inactive_time'].split()
            for t in time:
                if t.isnumeric():
                    inactive_time = inactive_time + t
                else:
                    inactive_time = inactive_time + " {} ".format(times[t])



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
