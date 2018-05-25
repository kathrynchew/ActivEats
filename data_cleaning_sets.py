# MEASURE NAMES / DESCRIPTORS / FRACTIONS for cleaning ingredient names out of
# strings

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
                     "liters", "qt", "qt.", "inch", "hunk"])

descriptors = set(["bulk", "store-bought", "finely", "diced", "chopped",
                   "coarse", "coarsely", "freshly", "sliced", "loose",
                   "of", "minced", "a", "store-bought", "brand",
                   "drops", "drop", "small", "of", "plus", "to", "few",
                   "bulk", "pure", "good", "quality", "thinly", "thickly",
                   "one", "name", "taste", "recipe", "gently", "storebought",
                   "strong", "little", "if", "desired", "cut", "into", "store",
                   "bought"])

fractions = set(["1/2", " 1/2", "1/4", "1/3", "3/4", "2/3", "1/8", "7/8", "1-",
                 "1/2-", "1/4-", "1/2-inch", "1/4-inch", "8-ounce",
                 "1-inch", "1/2-pound", "18-20", "dashes", "1-ounce",
                 "6-", "8-pound", "14.5-ounce" "6-ounce", "four",
                 "2-pound", "12-ounce", " 3", "1-pound", "#1", "pound/500",
                 "1/2-ounce", "1/o8-inch-think", "2-2", "4-ounces",
                 "2-1", "14-ounce", "1/4-ounce"])


# GRAM CONVERSIONS / FRACTION CONVERSIONS for cleaning ingredient quantities
# out of strings & converting them (where appropriate) to unified gram amounts

gram_conversions = {"teaspoon": 4.2,
                    "tablespoon": 14.3,
                    "cup": 340,
                    "ounce": 28.3,
                    "quart": 946.4,
                    "pound": 453.6
                    }

fraction_conversions = {"1/2": 0.5,
                        "1/4": 0.25,
                        "3/4": 0.75,
                        "1/3": 0.33,
                        "2/3": 0.66,
                        "1/8": 0.12,
                        "7/8": 0.87,
                        u'1\xbd': 1.5
                        }


# ACCEPTED UNITS: Units of measure for serving sizes/quantities

accepted_units = ['serving', 'servings', 'piece', 'pieces', 'cup', 'cups',
                  'dozen', 'square', 'squares', 'quart', 'quarts', 'portion',
                  'portions', 'pizza', 'pizzas', 'sandwich', 'sandwiches',
                  'cookie', 'cookies', 'pancake', 'panakes', 'bun', 'buns',
                  'truffle', 'truffles', 'burger', 'burgers', 'hors',
                  "d'oeuvres", 'pint', 'pints', 'cake', 'cakes', 'pie',
                  'pies']


# ACCEPTED MEASURES: Units of measure for ingredients

accepted_measures = {"teaspoon": "teaspoon",
                     "tsp": "teaspoon",
                     "tsp.": "teaspoon",
                     "teaspoons": "teaspoon",
                     "tablespoon": "tablespoon",
                     "tbsp": "tablespoon",
                     "tbsp.": "tablespoon",
                     "tablespoons": "tablespoon",
                     "cup": "cup",
                     "cups": "cup",
                     "ounce": "ounce",
                     "ounces": "ounce",
                     "oz": "ounce",
                     "oz.": "ounce",
                     "quart": "quart",
                     "quarts": "quart",
                     "qt": "quart",
                     "qt.": "quart",
                     "pound": "pound",
                     "pounds": "pound",
                     "lb": "pound",
                     "lb.": "pound",
                     }

# CATEGORY PREFERENCES: Names of category tags that are also user dietary preferences

category_preferences = ["Low Calorie", "Gluten Free", "Vegetarian", "Low-Carb",
                        "Vegan"]

# Tags for later expansion of dietary preferences
# category_preferences = ["Low Calorie", "Heart-Healthy", "Gluten Free",
#                         "Vegetarian", "Low-Cholesterol", "Low-Carb", "Low-Fat",
#                         "Vegan"]

# BREAKFAST / LUNCH / DINNER LISTS: Lists of category tag names used for filtering
# recipes to populate weekly meal plans

breakfast_list = ['Easy Breakfast Recipes', 'Healthy Breakfast', 'Brunch',
                  'Breakfast Casserole']

lunch_list = ['Lunch', 'Easy Lunch Recipes', 'Healthy Lunch', 'Main Dish',
              'Easy Main Dish']

dinner_list = ['Healthy Dinner', 'Easy Dinner Recipes', 'Main Dish',
               'Easy Main Dish']

breakfast_nums = [11, 21, 31, 41, 51]

lunch_nums = [12, 22, 32, 42, 52]

dinner_nums = [13, 23, 33, 43, 53]
