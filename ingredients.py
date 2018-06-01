# FUNCTIONS FOR HANDLING INGREDIENT CONSOLIDATION & CALCULATION FOR SHOPPING LISTS
from data_cleaning_sets import gram_conversions

def fetch_ingredients(collection):
    """ Unpacks ingredient names, amounts, units for an individual recipe """

    ingredient_list = []

    for key, value in collection.recipe.ingredient_amounts.items():
        if value is not None:
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


def get_shopping_list(breakfasts,lunches,dinners):
    """ Runs all functions to get final consolidated shopping list data """
    total_ingredients = consolidate_ingredients(breakfasts, lunches, dinners)
    final_ingredients = convert_ingredients(total_ingredients)

    return final_ingredients
