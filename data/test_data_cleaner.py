from sqlalchemy import func
from model import SampleFNRecipe, connect_to_db, db
from server import app
import json
import re


# Open JSON file & parse lines
with open("../scrapy/recipe_yum/recipe_yum/spiders/all_recipes_jsontest.json") as file:
    recipe_lines = json.load(file)

for line in recipe_lines:
    # ########################################################################
    # # INGREDIENTS: Populate value as an array; split into 2 additional columns
    # # of dict ingredient: qty (converted to grams) & text ingredients without
    # # amounts
    # measure_names = set(["cup", "cups", "teaspoon", "teaspoons", "tsp", "tsp.",
    #                      "tablespoon", "tablespoons", "tbsp", "tbsp.", "ounce",
    #                      "ounces", "oz", "oz.", "package", "pound", "pounds",
    #                      "small", "large", "container", "stalk", "stalks", "pinch",
    #                      "handful", "a handful", "stick", "sticks", "can", "quart",
    #                      "quarts", "dash", "pack", "sprig", "sprigs", "lb", "lb.",
    #                      "bag", "liter", "pieces"])

    # descriptors = set(["bulk", "store-bought", "finely", "diced", "chopped",
    #                    "coarse", "coarsely", "freshly", "sliced", "loose", "of",
    #                    "minced", "fresh", "a", "store-bought", "brand", "drops",
    #                    "drop", "small", "of", "plus", "to", "few", "bulk"])

    # fractions = set(["1/2", "1/4", "1/3", "3/4", "2/3", "1/8", "7/8", "1-",
    #              "1/2-", "1/4-", "1/2-inch", "1/4-inch", "8-ounce", "1-inch"])

    # # TEXT INGREDIENTS (written as in original text)
    # text_ingredients = line['ingredients']

    # # INGREDIENTS NAMES (cleaned of measures, numeric amounts, commentary)
    # if len(line['ingredients']) > 0:
    # ingredients_names = []

    # for item in line['ingredients']:
    #     item = re.sub(r" ?\([^)]+\)", "", item)
    #     item = item.lower().split(" ")
    #     item = [i for i in item if ((i.isnumeric() is False) and (i not in measure_names and i not in descriptors and i not in fractions))]
    #     print item
    #     item = " ".join(item).rstrip().encode('utf-8')
    #     item = item.split(',')
    #     item = item[0]
    #     ingredients_names.append(item)
    #     qty_data.add(item)

    # ingredients_names = Cast(ingredients_names, ARRAY(db.Text))

    #     else:
    #         ingredients_names = Cast(array([]), ARRAY(db.Text))


    # # INGREDIENTS QTY

    ########################################################################
    # SERVINGS: Split servings strings into 2 columns: servings_num (integer)
    # and servings_unit (text of serving unit/quantity)
    
    servings = line['servings']
    accepted_units = ['serving', 'servings', 'piece', 'pieces', 'cup', 'cups',
                      'dozen', 'square', 'squares', 'quart', 'quarts', 'portion',
                      'portions', 'pizza', 'pizzas', 'sandwich', 'sandwiches',
                      'cookie', 'cookies', 'pancake', 'panakes', 'bun', 'buns',
                      'truffle', 'truffles']

    if servings == 'N/A':
        servings_unit = None
        servings_num = None

    else:
        servings = re.sub(r" ?\([^)]+\)", "", servings)
        num = [i for i in servings.split() if i.isnumeric()] 
        unit = [i for i in servings.split() if (i.isnumeric() is False) and (i in accepted_units)]

        if num == []:
            servings_num = None
        else:
            servings_num = num[0]

        if unit == []:
            servings_unit = None
        else:
            servings_unit = unit

    print servings_num
    print servings_unit
