# FUNCTIONS FOR HANDLING INGREDIENT CONSOLIDATION & CALCULATION FOR SHOPPING LISTS
from data_cleaning_sets import gram_conversions


def fetch_ingredients(collection):
    """ Unpacks ingredient names, amounts, units for an individual Collection
    object (each Collection object contains only one recipe) """

    ingredient_list = []
    num_servings = collection.recipe.servings_num

    for key, value in collection.recipe.ingredient_amounts.items():
        if value is not None:
            if num_servings is not None:
                quantity = float(value)/num_servings
                data = [key, round(quantity, 2)]
            else:
                data = [key, round(float(value), 2)]
        else:
            data = [key, 0]
        ingredient_list.append(data)

    for item in ingredient_list:
        if item[0] in collection.recipe.ingredient_units:
            item.append(collection.recipe.ingredient_units[item[0]])
        else:
            item.append('N/A')

    return ingredient_list


def consolidate_ingredients(breakfasts, lunches, dinners):
    """ Finds duplicates of ingredients across multiple recipes and consolidates
    them into a single item with a combined quantity value """
    total_ingredients = {}
    meals = [breakfasts, lunches, dinners]

    for meal in meals:
        for collection in meal:
            ingredients = fetch_ingredients(collection)
            for lst in ingredients:
                if lst[0] in total_ingredients:
                    total_ingredients[lst[0]][0] += lst[1]
                    total_ingredients[lst[0]][1].add(lst[2])
                else:
                    total_ingredients[lst[0]] = [lst[1], set([lst[2]])]

    return total_ingredients


def convert_ingredients(total_ingredients):
    """ Creates alphabetical list of ingredients with aggregated quantity values
    converted from grams into appropriate 'cooking' units (e.g. cups, tbsp, etc) """
    final_ingredients = []

    for key, value in total_ingredients.items():
        unit = value[1].pop()
        if unit == 'N/A':
            final_ingredients.append([key, value[0], None])
        else:
            final_ingredients.append([key, round((value[0]/gram_conversions[unit]), 2), unit])

    return sorted(final_ingredients)


def get_shopping_list(breakfasts, lunches, dinners):
    """ Runs all functions to get final consolidated shopping list data """
    total_ingredients = consolidate_ingredients(breakfasts, lunches, dinners)
    final_ingredients = convert_ingredients(total_ingredients)

    return final_ingredients


def get_single_shopping_list(recipe):
    """ Consolidates ingredients from a single Recipe object into a list of
    lists, each sublist containing ingredient name, quantity in grams, and unit 
    values. Returns a list of lists with the following indices:

    [0] ingredient name (str)
    [1] quantity in grams (float)
    [2] units value (str) """
    total_ingredients = []

    for key, value in recipe.ingredient_amounts.items():
        if key in recipe.ingredient_units:
            unit = recipe.ingredient_units[key]
            total_ingredients.append([key, round((float(value)/gram_conversions[unit]), 2), unit])
        else:
            total_ingredients.append([key, value, None])

    return total_ingredients
