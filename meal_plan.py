# FUNCTIONS FOR HANDLING MEAL PLAN GENERATION
import random

def make_meal_set(meal_categories, user_prefs):
    """ Takes in two arguments. The second argument is a list of integers,
    corresponding to the category_ids of any dietary preferences specified by the
    user. The first argument is a list of all category objects to select recipes
    from (queried using SQLAlchemy to match the user's defined dietary preferences
    if applicable. If user has designated no preferences, the list of category
    objects is queried using SQLAlchemy to match the defined category tags in
    - data_cleaning_sets.breakfast_list,
    - data_cleaning_sets.lunch_list,
    - and data_cleaning_sets.dinner_list.

    Iterates through all recipes in each category, and all categories of each
    recipe, filtering for a recipe subset that match user-specified dietary
    preferences.

    Returns either a randomized set of five meals for that meal type, or in
    the case that there are not enough recipes that match the user's preferences
    to populate a full week's plan, propagates whatever recipes exist so the
    subset from which recipes are selected contains multiples of the existing
    recipe(s). """

    week_recipes = []

    for category in meal_categories:
        for recipe in category.recipe_categories:
            for other_cat in recipe.recipes.recipe_categories:
                # if other_cat.category_id in user_prefs:
                if other_cat.category_id in user_prefs:
                    week_recipes.append(recipe.recipes)

    if len(week_recipes) < 5:
        multiply_meals = []
        while len(multiply_meals) < 5:
            for item in week_recipes:
                multiply_meals.append(item)
        weekly_selection = random.sample(multiply_meals, 5)
    else:
        weekly_selection = random.sample(week_recipes, 5)

    return weekly_selection
