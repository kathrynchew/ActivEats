""" Recipes """

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory, Difficulty, RecipeDifficulty, User, UserPreference, Collection
import random
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
