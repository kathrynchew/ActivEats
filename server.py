""" Recipes """

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory, Difficulty, RecipeDifficulty, User, UserPreference, Collection
from data_cleaning_sets import breakfast_list, lunch_list, dinner_list
import random
from datetime import datetime
import pdb

app = Flask(__name__)

app.secret_key = "ITS_A_SECRET"

################################################################################
# ROUTES GO HERE

@app.route('/')
def display_dietary_preferences():
    """ Home page """
    # recipe = db.session.query(Category.category_name).filter_by(is_preference=True).all()
    recipe = Category.query.filter_by(is_preference=True).all()

    for item in recipe:
        # print item.recipe_categories
        for cat in item.recipe_categories:
            # print cat.recipes
            for obj in cat.recipes:
                print obj.recipe_name

    return render_template("home.html",
                           recipe=recipe)


@app.route('/test')
def display_recipe_formatting():
    """ Figure out how to display a recipe """
    recipe_id = random.randint(1, 990)

    recipe_text = Recipe.query.filter_by(recipe_id=recipe_id).first()

    print recipe_text.recipe_categories

    return render_template("display_recipe.html",
                           recipe_text=recipe_text)


@app.route('/recipes')
def display_recipe_list():
    """ Generate & display a complete list of recipe objects """
    all_recipes = Recipe.query.order_by('recipe_id').all()

    return render_template("recipes.html",
                           all_recipes=all_recipes)


@app.route('/recipes/<recipe_id>')
def recipe_page(recipe_id):
    """ Display the contents of a specific recipe """
    recipe_info = Recipe.query.filter_by(recipe_id=recipe_id).first()

    return render_template("display_recipe.html",
                           recipe_text=recipe_info)


@app.route('/my_week')
def display_current_meal_plan():
    """ If no meal plan currently exists, creates one. If meal plan already
    exits, displays the current week's meal plan """

    breakfast_recipes = []
    lunch_recipes = []
    dinner_recipes = []

    breakfast = Category.query.filter(Category.category_name.in_(breakfast_list)).all()
    lunch = Category.query.filter(Category.category_name.in_(lunch_list)).all()
    dinner = Category.query.filter(Category.category_name.in_(dinner_list)).all()

    for category in breakfast:
        for recipe in category.recipe_categories:
            breakfast_recipes.append(recipe.recipes)

    for category in lunch:
        for recipe in category.recipe_categories:
            lunch_recipes.append(recipe.recipes)

    for category in dinner:
        for recipe in category.recipe_categories:
            dinner_recipes.append(recipe.recipes)

    weekly_breakfasts = random.sample(breakfast_recipes, 5)
    weekly_lunches = random.sample(lunch_recipes, 5)
    weekly_dinners = random.sample(dinner_recipes, 5)

    print "Breakfast: "
    print weekly_breakfasts
    print "Lunch: "
    print weekly_lunches
    print "Dinner: "
    print weekly_dinners

    return render_template("meal_plan.html",
                           now=datetime.utcnow(),
                           breakfasts=weekly_breakfasts,
                           lunches=weekly_lunches,
                           dinners=weekly_dinners)



################################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
