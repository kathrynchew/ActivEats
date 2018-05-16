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
    # SampleFNRecipe.query.delete()


    urls_plus_ingredients = {}
    qty_data = set()

    for line in recipe_lines:
        if line['url'] == "http://www.foodnetwork.com/error-page/500":
            pass
        else:
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
            measure_names = set(["cup", "cups", "teaspoon", "teaspoons", "tsp",
                                 "tsp.", "tablespoon", "tablespoons", "tbsp",
                                 "tbsp.", "ounce", "ounces", "oz", "oz.", "package",
                                 "pound", "pounds", "small", "large", "container",
                                 "stalk", "stalks", "pinch", "handful", "a handful",
                                 "stick", "sticks", "can", "quart", "quarts",
                                 "dash", "pack", "sprig", "sprigs", "lb", "lb.",
                                 "bag", "liter", "pieces", "bags", "slices", "cans",
                                 "jar", "1/2cup", "cup/60ml", "box", "cans",
                                 "cup/250ml", "piece", "g", "pkg", "pkg.", "piece",
                                 "liters"])

            descriptors = set(["bulk", "store-bought", "finely", "diced", "chopped",
                               "coarse", "coarsely", "freshly", "sliced", "loose",
                               "of", "minced", "fresh", "a", "store-bought", "brand",
                               "drops", "drop", "small", "of", "plus", "to", "few",
                               "bulk", "pure", "good", "quality", "thinly", "thickly",
                               "one", "name", "taste", "recipe", "gently", "storebought",
                               "strong", "little", "if", "desired"])

            fractions = set(["1/2", " 1/2", "1/4", "1/3", "3/4", "2/3", "1/8", "7/8", "1-",
                             "1/2-", "1/4-", "1/2-inch", "1/4-inch", "8-ounce",
                             "1-inch", "1/2-pound", "18-20", "dashes", "1-ounce",
                             "6-", "8-pound", "14.5-ounce" "6-ounce", "four",
                             "2-pound", "12-ounce", " 3", "1-pound", "#1", "pound/500",
                             "1/2-ounce", "1/o8-inch-think", "2-2", "4-ounces",
                             "2-1", "14-ounce", "1/4-ounce"])

            # TEXT INGREDIENTS (written as in original text)
            text_ingredients = line['ingredients']

            # INGREDIENTS NAMES (cleaned of measures, numeric amounts, commentary)
            urls_plus_ingredients[url] = set()

            if len(line['ingredients']) > 0:
                ingredients_names = []

                for item in line['ingredients']:
                    item = re.sub(r" ?\([^)]+\)", "", item)
                    item = item.lower().split(" ")
                    item = [i for i in item if ((i.isnumeric() is False) and (len(i) > 0) and (i not in measure_names and i not in descriptors and i not in fractions))]
                    # print item
                    item = " ".join(item).rstrip().encode('utf-8')
                    item = item.split(',')
                    item = item[0]
                    if len(item) > 0:
                        ingredients_names.append(item)
                        qty_data.add(item)
                        urls_plus_ingredients[url].add(item)
                        # print recipe_name, ingredients_names

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
            # import pdb; pdb.set_trace()

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
            # print recipe

    ############################################################################
    # COMMIT: Commit all changes (objects added) to database.

    db.session.commit()
    return [urls_plus_ingredients, qty_data]

################################################################################
############################### LOAD INGREDIENTS ###############################
################################################################################
def load_ingredients(qty_data):
    """ Load ingredients into INGREDIENT_ATTRIBUTES table """

    print "Adding Ingredient"

    # Delete all rows in table, so sample table can be created repeatedly with
    # new data and no duplicates
    Ingredient.query.delete()

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
            # print ingredient

    db.session.commit()


################################################################################
############################# ASSOCIATION TABLE ################################
################################################################################
def load_recipe_ingredients(urls_plus_ingredients):
    """ Populate association table of recipes to ingredients in each recipe """

    print "Adding All Recipe/Ingredient Associations"

    RecipeIngredient.query.delete()

    all_recipe_ids = db.session.query(SampleFNRecipe.recipe_id, SampleFNRecipe.recipe_url).all()

    for pair in all_recipe_ids:
        recipe_url = pair[1]
        for item in urls_plus_ingredients[recipe_url]:
            ingredient_name = item
            ingredient_id = Ingredient.query.filter_by(ingredient_name=ingredient_name).first().ingredient_id

            recipe_ingredient = RecipeIngredient(recipe_id=pair[0],
                                                 ingredient_id=ingredient_id)

            db.session.add(recipe_ingredient)

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
    urls_plus_ingredients, qty_data = load_recipes()
    load_ingredients(qty_data)
    load_recipe_ingredients(urls_plus_ingredients)
    # set_val_recipe_id()
