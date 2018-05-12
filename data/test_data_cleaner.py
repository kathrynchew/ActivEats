from sqlalchemy import func
from model import SampleFNRecipe, connect_to_db, db
from server import app
import json
import re


# Open JSON file & parse lines
with open("../scrapy/recipe_yum/recipe_yum/spiders/all_recipes_jsontest.json") as file:
    recipe_lines = json.load(file)

for line in recipe_lines:
    ########################################################################
    # INGREDIENTS: Populate value as an array; split into 2 additional columns
    # of dict ingredient: qty (converted to grams) & text ingredients without
    # amounts
    measure_names = ["cup", "cups", "teaspoon", "teaspoons", "tsp", "tsp.",
                     "tablespoon", "tablespoons", "tbsp", "tbsp.", "ounce",
                     "ounces", "oz", "oz.", "package", "pound", "pounds",
                     "small", "large", "container", "stalk", "stalks", "pinch",
                     "a pinch", "handful", "a handful", "few", "a few", "to",
                     "plus", "of", "stick", "sticks", "can", "quart", "quarts",
                     "dash", "pack", "sprig", "sprigs", "lb", "lb.", "bag",
                     "liter", "bulk", "pieces"]

    descriptors = ["bulk", "store-bought", "finely", "diced", "chopped",
                   "coarse", "coarsely", "freshly", "sliced", "loose", "of",
                   "minced", "fresh", "a", "store-bought", "brand", "drops",
                   "drop", "small"]

    fractions = ["1/2", "1/4", "1/3", "3/4", "2/3", "1/8", "7/8", "1-",
                 "1/2-", "1/4-", "1/2-inch", "1/4-inch", "8-ounce", "1-inch"]

    # TEXT INGREDIENTS (written as in original text)
    text_ingredients = line['ingredients']

    # INGREDIENTS NAMES (cleaned of measures, numeric amounts, commentary)
    # if len(line['ingredients']) > 0:
    ingredients_names = []

    for item in line['ingredients']:
        item = re.sub(r" ?\([^)]+\)", "", item)
        item = item.lower().split(" ")
        for i in item:
            if i.isnumeric():
                item.remove(i)
        print item
        for i in item:
            if i in measure_names:
                item.remove(i)
        print item
        for i in item:
            if i in descriptors:
                item.remove(i)
        print item
        for i in item:
            if i in fractions:
                item.remove(i)
        print item
        item = " ".join(item).rstrip().encode('utf-8')
        item = item.split(',')
        item = item[0]
        ingredients_names.append(item)
        # qty_data.add(item)

    # ingredients_names = Cast(ingredients_names, ARRAY(db.Text))
    print ingredients_names

        # else:
            # ingredients_names = Cast(array([]), ARRAY(db.Text))


    # INGREDIENTS QTY
