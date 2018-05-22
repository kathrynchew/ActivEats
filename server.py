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
    # recipe = Category.query.filter_by(is_preference=True).all()
    recipe_id = random.randint(1, 990)

    featured_recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()

    while not featured_recipe.photo_url:
        recipe_id = random.randint(1, 990)
        featured_recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()

    # for item in recipe:
    #     # print item.recipe_categories
    #     for cat in item.recipe_categories:
    #         # print cat.recipes
    #         for obj in cat.recipes:
    #             print obj.recipe_name

    return render_template("home.html",
                           recipe=featured_recipe)


@app.route('/test')
def display_recipe_formatting():
    """ Figure out how to display a recipe """
    recipe_id = random.randint(1, 990)

    recipe_text = Recipe.query.filter_by(recipe_id=recipe_id).first()

    print recipe_text.recipe_categories

    return render_template("display_recipe.html",
                           recipe_text=recipe_text)


@app.route('/login')
def login_or_register():
    """ Display form to allow users to login or register for an account """

    return render_template("login_register.html")


@app.route('/welcome', methods=["GET"])
def welcome_login():
    """ If person attempts to log in to an existing account, assesses if they
    have an account. If so, logs them in. If not, flashes a message to alert
    user to register or re-enter credentials correctly """

    email = request.args.get('email')
    password = request.args.get('password')

    query_email = User.query.filter_by(email=email).first()

    if query_email:
        if query_email.password == password:
            flash("You have successfully logged in!")
            return redirect("/")
        else:
            flash("The password is incorrect. Please try again.")
            return redirect("/login")
    else:
        flash("There is no account associated with that email. Please try again.")
        return redirect("/login")


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


@app.route('/categories/<category_id>')
def category_page(category_id):
    """ Display all recipes in a specific category """
    category_info = Category.query.filter_by(category_id=category_id).first()

    return render_template("display_category.html",
                           category_info=category_info)


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

    return render_template("meal_plan.html",
                           now=datetime.utcnow(),
                           breakfasts=weekly_breakfasts,
                           lunches=weekly_lunches,
                           dinners=weekly_dinners)


@app.route('/search')
def display_search_results():
    """ Displays any results from a recipe search """

    search_term = request.args.get('search_term')
    cleaned_term = search_term[:-1].title()

    search_results_names = Recipe.query.filter(Recipe.recipe_name.like("%{}%".format(cleaned_term))).all()
    search_results_categories = Category.query.filter(Category.category_name.like("%{}%".format(cleaned_term))).all()

    print search_results_names
    print search_results_categories
    print "yo bro"

    return render_template("search_results.html",
                           recipes=search_results_names,
                           categories=search_results_categories,
                           search_term=search_term)



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
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    app.run(port=5000, host='0.0.0.0')
