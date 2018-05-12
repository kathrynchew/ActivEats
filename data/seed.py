""" Utility file to clean & seed recipe database from scraped data """

from sqlalchemy import func
from model import SampleFNRecipe, Ingredient, connect_to_db, db
from server import app
import json
import re
from sqlalchemy.dialects.postgresql import array, ARRAY
from sqlalchemy.sql.functions import Cast


# Open JSON file & parse lines
with open("../scrapy/recipe_yum/recipe_yum/spiders/all_recipes_jsontest.json") as file:
    recipe_lines = json.load(file)

################################################################################
################################# LOAD RECIPES #################################
################################################################################
def load_recipes():
    """ Load recipes into FOOD_NETWORK_INSPECT table """

    print "Adding SampleFNRecipe"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    SampleFNRecipe.query.delete()

    qty_data = set()

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
        # INGREDIENTS: Populate value as an array; split into 2 additional columns
        # of dict ingredient: qty (converted to grams) & text ingredients without
        # amounts
        measure_names = ["cup", "cups", "teaspoon", "teaspoons", "tsp", "tsp.",
                         "tablespoon", "tablespoons", "tbsp", "tbsp.", "ounce",
                         "ounces", "oz", "oz.", "package", "pound", "pounds",
                         "small", "large", "container", "stalk", "stalks", "pinch",
                         "a pinch", "handful", "a handful", "few", "a few", "to",
                         "plus", "of", "stick", "sticks", "drop", "drops", "can",
                         "dash", "pack", "sprig", "sprigs", "lb", "lb.", "bag",
                         "liter", "bulk", "pieces"]

        descriptors = ["bulk", "store-bought", "finely", "diced", "chopped",
                       "coarse", "coarsely", "freshly", "sliced", "loose", "of",
                       "minced", "fresh", "a", "store-bought", "brand"]

        fractions = ["1/2", "1/4", "1/3", "3/4", "2/3", "1/8", "7/8", "1-",
                     "1/2-", "1/4-", "1/2-inch", "1/4-inch", "8-ounce"]

        # TEXT INGREDIENTS (written as in original text)
        text_ingredients = line['ingredients']

        # INGREDIENTS NAMES (cleaned of measures, numeric amounts, commentary)
        if len(line['ingredients']) > 0:
            ingredients_names = []

            for item in line['ingredients']:
                item = re.sub(r" ?\([^)]+\)", "", item)
                item = item.lower().split(" ")
                for i in item:
                    if i.isnumeric():
                        item.remove(i)
                for i in item:
                    if i in measure_names:
                        item.remove(i)
                for i in item:
                    if i in descriptors:
                        item.remove(i)
                for i in item:
                    if i in fractions:
                        item.remove(i)
                item = " ".join(item).rstrip().encode('utf-8')
                item = item.split(',')
                item = item[0]
                ingredients_names.append(item)
                qty_data.add(item)

            ingredients_names = Cast(ingredients_names, ARRAY(db.Text))

        else:
            ingredients_names = Cast(array([]), ARRAY(db.Text))

        # INGREDIENTS QTY ()


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


        ########################################################################
        # CREATE OBJECT: Declare object, declare all column values, add object
        # to database, rise & repeat.


        recipe = SampleFNRecipe(recipe_name=recipe_name,
                                recipe_author=recipe_author,
                                category_tags=category_tags,
                                difficulty=difficulty,
                                servings=servings,
                                special_equipment=special_equipment,
                                text_ingredients=text_ingredients,
                                ingredients_names=ingredients_names,
                                preparation=preparation,
                                total_time=total_time,
                                prep_time=prep_time,
                                cook_time=cook_time,
                                active_time=active_time,
                                inactive_time=inactive_time,
                                photo_url=photo_url,
                                recipe_url=url)

        db.session.add(recipe)

    ############################################################################
    # COMMIT: Commit all changes (objects added) to database.

    db.session.commit()
    return qty_data

################################################################################
############################### LOAD INGREDIENTS ###############################
################################################################################
def load_ingredients(qty_data):
    """ Load ingredients into INGREDIENT_ATTRIBUTES table """

    print "Adding Ingredient"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    SampleFNRecipe.query.delete()

    for item in qty_data:
        ingredient_name = item
        whole_grams = 100
        calories_per_whole = None
        carbs_per_whole = None
        sugar_per_whole = None

        ingredient = Ingredient(ingredient_name=ingredient_name,
                                whole_grams=whole_grams,
                                calories_per_whole=calories_per_whole,
                                carbs_per_whole=carbs_per_whole,
                                sugar_per_whole=sugar_per_whole)

        db.session.add(ingredient)

    db.session.commit()

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# def set_val_recipe_id():
#     """Set value for the next recipe_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(SampleFNRecipe.recipe_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('samplerecipes_recipe_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()



################################################################################
# HELPER FUNCTIONS

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    qty_data = load_recipes()
    load_ingredients(qty_data)
    # set_val_recipe_id()
