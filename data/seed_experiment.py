""" Utility file to clean & seed recipe database from scraped data """

from sqlalchemy import func
from model import SampleFNRecipe, Ingredient, RecipeIngredient, connect_to_db, db
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

    individual_ingredients = set()
    ingredients_per_recipe = {}

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
        # INGREDIENTS: Populate value as an array; split into 2 additional
        # columns of dict ingredient: qty (converted to grams) & text
        # ingredients without amounts
        measure_names = set(["cup", "cups", "teaspoon", "teaspoons", "tsp",
                             "tsp.", "tablespoon", "tablespoons", "tbsp",
                             "tbsp.", "ounce", "ounces", "oz", "oz.", "package",
                             "pound", "pounds", "small", "large", "container",
                             "stalk", "stalks", "pinch", "handful", "a handful",
                             "stick", "sticks", "can", "quart", "quarts",
                             "dash", "pack", "sprig", "sprigs", "lb", "lb.",
                             "bag", "liter", "pieces"])

        descriptors = set(["bulk", "store-bought", "finely", "diced", "chopped",
                           "coarse", "coarsely", "freshly", "sliced", "loose",
                           "of", "minced", "fresh", "a", "store-bought", "brand",
                           "drops", "drop", "small", "of", "plus", "to", "few",
                           "bulk", "pure", "good", "quality", "thinly", "thickly",
                           "one"])

        fractions = set(["1/2", "1/4", "1/3", "3/4", "2/3", "1/8", "7/8", "1-",
                         "1/2-", "1/4-", "1/2-inch", "1/4-inch", "8-ounce",
                         "1-inch", "1/2-pound"])

        # TEXT INGREDIENTS (written as in original text)
        text_ingredients = line['ingredients']
        # line['ingredients'] is an array of strings (pulled from single line of overall json doc)

        # INGREDIENTS NAMES (cleaned of measures, numeric amounts, commentary)
        # If line['ingredients'] has any contents, do the following
        if len(line['ingredients']) > 0:
            # ingredients_names = []
            # ingredients_per_recipe = set()
            ingredients_per_recipe[url] = set()

            # item is a single string
            for item in line['ingredients']:
                # use regex to remove all text contained in parentheses ()
                item = re.sub(r" ?\([^)]+\)", "", item)
                # apply string method lower, split into array of individual words (on spaces)
                item = item.lower().split(" ")
                # list comprehension; return all words from word array that are NOT numeric and NOT in any of the 3 lists above
                item = [i for i in item if ((i.isnumeric() is False) and (i not in measure_names and i not in descriptors and i not in fractions))]
                # rejoin words from word array using spaces; rstrip any blanks/newlines, encode in utf-8
                item = " ".join(item).rstrip().encode('utf-8')
                # re-split string on commas; redeclare "item" to be equal to only the first clause (drop any commentary)
                item = item.split(',')
                item = item[0]
                # append "item" to list of ingredient names (kept in same table)
                ingredients_names.append(item)
                # add "item" to set of individual ingredients (to return for use in other tables)
                individual_ingredients.add(item)
                # add "item" to ingredients_per_recipe set as a tuple with recipe_name to populate intermediate table
                # ingredients_per_recipe.add((line['recipe_name'], item))
                ingredients_per_recipe[url].add(item)

            # Typecast list of ingredient names (for the single recipe) as SQL ARRAY type
            ingredients_names = Cast(ingredients_names, ARRAY(db.Text))

        # if line['ingredients'] has no contents, typecast (empty) list of ingredient names to SQL ARRAY type
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
        # CREATE MIDDLE TABLE OBJECT: Declare object, declare column values, add
        # object to recipe_ingredients table, rinse & repeat.

        # for item in ingredients_per_recipe:
        #     rec_ing = RecipeIngredient(recipe_name=item[0],
        #                                ingredient_name=item[1])
        #     db.session.add(rec_ing)

        ########################################################################
        # CREATE OBJECT: Declare object, declare all column values, add object
        # to database, rinse & repeat.


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

        # for item in individual_ingredients:
        #     ingredient_tuple = (url, item)
        #     ingredients_per_recipe.add(ingredient_tuple)

    ############################################################################
    # COMMIT: Commit all changes (objects added) to database.

    db.session.commit()

    # print ingredients_per_recipe
    return ingredients_per_recipe

################################################################################
############################### LOAD INGREDIENTS ###############################
################################################################################
def load_ingredients(ingredients_per_recipe):
    """ Load ingredients into INGREDIENT_ATTRIBUTES table """

    print "Adding Ingredient"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    SampleFNRecipe.query.delete()

    for value in ingredients_per_recipe:
        for item in value:
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
            print "Ingredient Added"

    db.session.commit()


def load_recipe_ingredients(ingredients_per_recipe):
    """ Load ingredient/recipe relationships in RECIPE_INGREDIENTS table """

    print "Adding Recipe/Ingredient Relationshps"

    for key, value in ingredients_per_recipe:
        recipe_url = key
        for item in value:
            ingredient_name = item
            relationship = RecipeIngredient(recipe_url=recipe_url,
                                            ingredient_name=ingredient_name)

            db.session.add(relationship)

    db.session.commit()

        # ingredient_id = Ingredient.query.filter_by(ingredient_name=item[1]).first().ingredient_id
        # recipe_id = SampleFNRecipe.query.filter_by(url=item[0]).first().recipe_id

        # relationship = RecipeIngredient(ingredient_id=ingredient_id,
                                        # recipe_id=recipe_id)
        # db.session.add(relationship)

    # db.session.commit()

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
    ingredients_per_recipe = load_recipes()
    load_ingredients(ingredients_per_recipe)
    load_recipe_ingredients(ingredients_per_recipe)
    # set_val_recipe_id()
