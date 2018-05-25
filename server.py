""" Recipes """

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory, Difficulty, RecipeDifficulty, User, UserPreference, Collection
from data_cleaning_sets import breakfast_list, lunch_list, dinner_list
import random
import datetime
import time
import pdb

app = Flask(__name__)

app.secret_key = "ITS_A_SECRET"

################################################################################
# ROUTES GO HERE

@app.route('/')
def display_featured_recipe():
    """ Home page """
    recipe_id = random.randint(1, 990)

    featured_recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()

    while not featured_recipe.photo_url:
        recipe_id = random.randint(1, 990)
        featured_recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()

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


@app.route('/logout')
def logout_user():
    """ Log user out, delete their info from the session """

    session['username'] = None
    session['user_id'] = None

    flash("You have logged out. Goodbye!")
    return redirect('/')


@app.route('/welcome', methods=["GET"])
def welcome_login():
    """ If person attempts to log in to an existing account, assesses if they
    have an account. If so, logs them in. If not, flashes a message to alert
    user to register or re-enter credentials correctly """

    email = request.args.get('email')
    password = request.args.get('password')

    print email
    print password

    queried_user = User.query.filter_by(email=email).first()

    print queried_user

    if queried_user:
        if queried_user.password == password:
            flash("You have successfully logged in!")
            session['username'] = queried_user.username
            session['user_id'] = queried_user.user_id
            return redirect("/")
        else:
            flash("The password is incorrect. Please try again.")
            return redirect("/login")
    else:
        flash("There is no account associated with that email. Please try again.")
        return redirect("/login")


@app.route('/welcome', methods=["POST"])
def welcome_register():
    """ If person attempts to create a new account, processes their data to create
    account and log them in. Flashes message of success when complete """

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    prefs = request.form.getlist('prefs')

    print prefs

    new_user = User(username=username,
                    email=email,
                    password=password)

    db.session.add(new_user)
    db.session.commit()

    user_prefs = Category.query.filter(Category.category_name.in_(prefs)).all()
    print user_prefs
    added_user = User.query.filter_by(email=email).first()

    print added_user
    print added_user.user_id

    for item in user_prefs:
        new_pref = UserPreference(user_id=added_user.user_id,
                                  category_id=item.category_id)

        db.session.add(new_pref)
        db.session.commit()

    session['username'] = added_user.username
    session['user_id'] = added_user.user_id
    flash("You have successfully created an account!")
    return redirect("/")


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

    now = datetime.date.today().strftime("%W")
    print now

    return render_template("meal_plan.html",
                           now=now,
                           breakfasts=weekly_breakfasts,
                           lunches=weekly_lunches,
                           dinners=weekly_dinners)


@app.route('/search')
def display_search_results():
    """ Displays any results from a recipe search """

    search_term = request.args.get('search_term')

    if search_term[-1].lower() == "s":
        cleaned_term = search_term[:-1].title()
    else:
        cleaned_term = search_term.title()

    search_results_names = Recipe.query.filter(Recipe.recipe_name.like("%{}%".format(cleaned_term))).all()
    search_results_categories = Category.query.filter(Category.category_name.like("%{}%".format(cleaned_term))).all()

    print search_results_names
    print search_results_categories
    print "yo bro"

    return render_template("search_results.html",
                           recipes=search_results_names,
                           categories=search_results_categories,
                           search_term=search_term)


@app.route('/preferences/<user_id>')
def display_user_preferences(user_id):
    """ Displays user's current dietary preferences & profile information (email,
        password) & allows users to update or change """
    # user_id = request.args.get('user_id')

    user_info = User.query.filter_by(user_id=user_id).first()

    return render_template("preferences.html",
                           user_info=user_info)


@app.route('/preferences/edit', methods=["POST"])
def edit_user_preferences():
    """ Updates user's dietary preferences """
    user_id = session['user_id']
    prefs_post = dict(request.form)
    # new_prefs = request.get_json()

    new_prefs = []
    for pref in prefs_post['prefs[]']:
        new_prefs.append(pref)

    print new_prefs
    # print new_prefs['prefs']

    print "ALL DA BUTTS"

    new_pref_categories = Category.query.filter(Category.category_name.in_(new_prefs)).all()
    current_prefs = UserPreference.query.filter_by(user_id=user_id).all()
    current_pref_categories = UserPreference.query.filter(UserPreference.user_id == user_id).all()

    for item in new_pref_categories:
        print item
        if item.category_id in current_pref_categories:
            continue
        else:
            update_pref = UserPreference(user_id=user_id,
                                         category_id=item.category_id)
            db.session.add(update_pref)

    for pref in current_prefs:
        if pref.category.category_name in new_prefs:
            continue
        else:
            db.session.delete(pref)

    db.session.commit()

    updated_prefs = User.query.filter_by(user_id=user_id).first()

    print updated_prefs
    # return updated_prefs



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

    # Stop the Debbugger from freaking out every time there is a redirect
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
