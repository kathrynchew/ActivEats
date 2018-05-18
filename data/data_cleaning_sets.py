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
                   "strong", "little", "if", "desired", "cut", "into"])

fractions = set(["1/2", " 1/2", "1/4", "1/3", "3/4", "2/3", "1/8", "7/8", "1-",
                 "1/2-", "1/4-", "1/2-inch", "1/4-inch", "8-ounce",
                 "1-inch", "1/2-pound", "18-20", "dashes", "1-ounce",
                 "6-", "8-pound", "14.5-ounce" "6-ounce", "four",
                 "2-pound", "12-ounce", " 3", "1-pound", "#1", "pound/500",
                 "1/2-ounce", "1/o8-inch-think", "2-2", "4-ounces",
                 "2-1", "14-ounce", "1/4-ounce"])

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
                        "7/8": 0.87
                        }

accepted_units = ['serving', 'servings', 'piece', 'pieces', 'cup', 'cups',
      'dozen', 'square', 'squares', 'quart', 'quarts', 'portion',
      'portions', 'pizza', 'pizzas', 'sandwich', 'sandwiches',
      'cookie', 'cookies', 'pancake', 'panakes', 'bun', 'buns',
      'truffle', 'truffles', 'burger', 'burgers', 'hors',
      "d'oeuvres", 'pint', 'pints', 'cake', 'cakes', 'pie',
      'pies']