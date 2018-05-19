""" Utility file to clean & seed recipe database from scraped data """

from sqlalchemy import func
from model import Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory, Difficulty, RecipeDifficulty, connect_to_db, db
from server import app
import json
import re
from unicodedata import numeric
from sqlalchemy.dialects.postgresql import array, ARRAY, JSON
from sqlalchemy.sql.functions import Cast
from data_cleaning_sets import measure_names, descriptors, fractions, gram_conversions, fraction_conversions, accepted_units, accepted_measures


# Open JSON file & parse lines
with open("recipe_files/all_recipes_jsontest.json") as file:
    recipe_lines = json.load(file)

################################################################################
################################# LOAD RECIPES #################################
################################################################################
def load_recipes():
    """ Load recipes into RECIPES table """

    print "Adding Recipes"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    # Recipe.query.delete()

    urls_plus_ingredients = {}
    qty_data = set()
    urls_plus_categories = {}
    raw_tags = set()
    urls_plus_difficulty = {}
    difficulty_types = set()

    for line in recipe_lines:
        if line['url'] == "http://www.foodnetwork.com/error-page/500":
            pass
        else:
            url = line['url']
            difficulty = "".join(line['difficulty'])
            recipe_name = line['recipe_name']
            recipe_author = line['recipe_author']
            photo_url = line['photo_url']


            ########################################################################
            # CATEGORY TAGS: Transfer scraped category arrays to a set to return
            # for further processing in LOAD_TAGS function.

            urls_plus_categories[url] = set()

            for item in line['category_tags']:
                if len(item) > 0:
                    raw_tags.add(item)
                    urls_plus_categories[url].add(item)

            ########################################################################
            # DIFFICULTY LEVELS: Transfer scraped difficulty strings to a set to return
            # for further processing in LOAD_DIFFICULTY function.

            if difficulty != 'N/A':
                urls_plus_difficulty[url] = difficulty
                difficulty_types.add(difficulty)


            ########################################################################
            # SERVINGS: Split servings strings into 2 columns: servings_num (integer)
            # and servings_unit (text of serving unit/quantity)

            servings = line['servings']

            if servings == 'N/A':
                servings_unit = None
                servings_num = None

            else:
                servings = re.sub(r" ?\([^)]+\)", "", servings)
                num = [i for i in servings.split() if i.isnumeric()]
                unit = [i for i in servings.lower().split() if (i.isnumeric() is False) and (i in accepted_units)]

                if num == []:
                    servings_num = None
                else:
                    servings_num = num[0]

                if unit == []:
                    servings_unit = None
                else:
                    servings_unit = " ".join(unit)

            text_servings = line['servings']


            ########################################################################
            # INGREDIENTS: Populate value as an array; split into 2 additional columns
            # of dict ingredient: qty (converted to grams) & text ingredients without
            # amounts

            # TEXT INGREDIENTS (written as in original text)
            text_ingredients = line['ingredients']

            # INGREDIENTS NAMES (cleaned of measures, numeric amounts, commentary)
            urls_plus_ingredients[url] = set()
            ingredient_amounts = {}
            ingredient_units = {}

            if len(line['ingredients']) > 0:

                for item in line['ingredients']:
                    item = re.sub(r" ?\([^)]+\)", "", item)
                    item = item.lower().split(" ")
                    amt = [i for i in item if i.isnumeric() or i in fraction_conversions]

                    if len(amt) > 0:
                        if amt[0] in fraction_conversions:
                            amt = [fraction_conversions[amt[0]]]
                        if len(amt) > 1:
                            if amt[1] in fraction_conversions:
                                amt = [float(amt[0]) + fraction_conversions[amt[1]]]
                            else:
                                amt = amt[:1]
                    else:
                        amt = None

                    unit = [i for i in item if (i in accepted_measures)]

                    if len(unit) > 0:
                        unit = accepted_measures[unit[0]]
                    else:
                        unit = None

                    item = [i for i in item if ((i.isnumeric() is False) and (len(i) > 0) and (i not in measure_names and i not in descriptors and i not in fractions))]
                    item = " ".join(item).rstrip().encode('utf-8')
                    item = item.split(',')
                    item = item[0]
                    if len(item) > 0:
                        qty_data.add(item)
                        urls_plus_ingredients[url].add(item)

            # INGREDIENTS QTY (uses cleaned ingredient names as keys; converts
            # amounts to grams for consistency; also tracks corresponding units)
                        if item not in ingredient_amounts:
                            if amt is not None and len(amt) > 0:
                                if unit is not None:
                                    amt = amt[0]
                                    if type(amt) != float and not amt.isdigit():
                                        amt = numeric(amt)
                                    ingredient_amounts[item] = round((float(amt) * gram_conversions[unit]), 2)
                                else:
                                    amt = amt[0]
                                    if type(amt) != float and not amt.isdigit():
                                        amt = numeric(amt)
                                    ingredient_amounts[item] = amt
                            else:
                                ingredient_amounts[item] = None

                        # Add ingredient units to ingredient_units dictionary
                        if item not in ingredient_units:
                            if unit is not None:
                                ingredient_units[item] = unit


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

            recipe = Recipe(recipe_name=recipe_name,
                            recipe_author=recipe_author,
                            servings_num=servings_num,
                            servings_unit=servings_unit,
                            text_servings=text_servings,
                            special_equipment=special_equipment,
                            text_ingredients=text_ingredients,
                            ingredient_amounts=ingredient_amounts,
                            ingredient_units=ingredient_units,
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

    return [urls_plus_ingredients, qty_data, urls_plus_categories, raw_tags,
            urls_plus_difficulty, difficulty_types]

################################################################################
############################### LOAD INGREDIENTS ###############################
################################################################################
def load_ingredients(qty_data):
    """ Load ingredients into INGREDIENT_ATTRIBUTES table """

    print "Adding Ingredients"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    # Ingredient.query.delete()

    for item in qty_data:
        if len(item) == 0:
            pass
        else:
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
################################# LOAD TAGS ####################################
################################################################################
def load_tags(raw_tags):
    """ Load category tags into CATEGORY_TAGS table """

    print "Adding Category Tags"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    # Category.query.delete()

    for item in raw_tags:
        category_name = item

        category = Category(category_name=category_name)

        db.session.add(category)

    db.session.commit()


################################################################################
################################ LOAD DIFFICULTY ###############################
################################################################################
def load_difficulty(difficulty_types):
    """ Load difficulty levels into DIFFICULTY_LEVELS table """

    print "Adding Difficulty Level Data"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    # Difficulty.query.delete()

    for item in difficulty_types:
        difficulty_level = item

        level = Difficulty(difficulty_level=difficulty_level)

        db.session.add(level)

    db.session.commit()


################################################################################
############################# ASSOCIATION TABLES ###############################
################################################################################

# Query all recipe_id entries from RECIPES table for reference in
# constructing all association tables

# Build association tables
def load_recipe_ingredients(urls_plus_ingredients):
    """ Populate association table of recipes to ingredients in each recipe """

    print "Adding All Recipe/Ingredient Associations"

    # RecipeIngredient.query.delete()

    all_recipe_ids = db.session.query(Recipe.recipe_id, Recipe.recipe_url).all()

    for pair in all_recipe_ids:
        recipe_url = pair[1]
        for item in urls_plus_ingredients[recipe_url]:
            ingredient_name = item
            ingredient_id = Ingredient.query.filter_by(ingredient_name=ingredient_name).first().ingredient_id

            recipe_ingredient = RecipeIngredient(recipe_id=pair[0],
                                                 ingredient_id=ingredient_id)

            db.session.add(recipe_ingredient)

    db.session.commit()


def load_recipe_categories(urls_plus_categories):
    """ Populate association table of recipes to category tags describing each
    recipe """

    print "Adding All Recipe/Category Associations"

    # RecipeCategory.query.delete()

    all_recipe_ids = db.session.query(Recipe.recipe_id, Recipe.recipe_url).all()

    for pair in all_recipe_ids:
        recipe_url = pair[1]
        for item in urls_plus_categories[recipe_url]:
            category_name = item
            category_id = Category.query.filter_by(category_name=category_name).first().category_id

            recipe_category = RecipeCategory(recipe_id=pair[0],
                                             category_id=category_id)

            db.session.add(recipe_category)

    db.session.commit()


def load_recipe_difficulty(urls_plus_difficulty):
    """ Populate association table of recipe to difficulty level of preparing
    that recipe """

    print "Adding All Recipe/Difficulty Level Associations"

    # RecipeDifficulty.query.delete()

    all_recipe_ids = db.session.query(Recipe.recipe_id, Recipe.recipe_url).order_by(Recipe.recipe_id).all()

    for pair in all_recipe_ids:
        recipe_url = pair[1]
        if recipe_url in urls_plus_difficulty:
            difficulty_level = urls_plus_difficulty[recipe_url]
            difficulty_id = Difficulty.query.filter_by(difficulty_level=difficulty_level).first().difficulty_id

            recipe_difficulty = RecipeDifficulty(recipe_id=pair[0],
                                                 difficulty_id=difficulty_id)

            db.session.add(recipe_difficulty)

    db.session.commit()


################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# def set_val_recipe_id():
#     """Set value for the next recipe_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(Recipe.recipe_id)).one()
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
    urls_plus_ingredients, qty_data, urls_plus_categories, raw_tags, urls_plus_difficulty, difficulty_types = load_recipes()
    load_ingredients(qty_data)
    load_tags(raw_tags)
    load_difficulty(difficulty_types)
    load_recipe_ingredients(urls_plus_ingredients)
    load_recipe_categories(urls_plus_categories)
    load_recipe_difficulty(urls_plus_difficulty)

    # set_val_recipe_id()
