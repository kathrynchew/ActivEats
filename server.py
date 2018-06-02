""" Recipes """

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db, db, Recipe, Ingredient, RecipeIngredient,
                   Category, RecipeCategory, Difficulty, RecipeDifficulty, User,
                   UserPreference, Collection)
from data_cleaning_sets import (gram_conversions, breakfast_list, lunch_list,
                                dinner_list)
from flask_mail import Mail, Message
from isoweek import Week
import os
import ingredients
import random
import datetime
import time
import pdb

app = Flask(__name__)

app.secret_key = "ITS_A_SECRET"

# APP CONFIG SETTINGS FOR FLASK-MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

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


@app.route('/welcome/login', methods=["POST"])
def welcome_login():
    """ If person attempts to log in to an existing account, assesses if they
    have an account. If so, logs them in. If not, flashes a message to alert
    user to register or re-enter credentials correctly """

    email = request.form.get('email')
    password = request.form.get('password')

    queried_user = User.query.filter_by(email=email).first()

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

    shopping_list = ingredients.get_single_shopping_list(recipe_info)

    return render_template("display_recipe.html",
                           recipe_text=recipe_info,
                           shopping_list=shopping_list)


@app.route('/categories/<category_id>')
def category_page(category_id):
    """ Display all recipes in a specific category """
    category_info = Category.query.filter_by(category_id=category_id).first()

    return render_template("display_category.html",
                           category_info=category_info)


@app.route('/my_week')
def display_current_meal_plan():
    """ If no meal plan currently exists, creates one. If meal plan already
    exits, displays the current week's meal plan

    Collection attribute 'set_number' is a concat of current year, week of year,
    i.e. YYYYWW

    Collection attribute 'set_day' is a single digit indicating the number of the
    day of the week to which it corresponds, i.e. 1 == Monday, 2 == Tuesday, etc. """

    week = datetime.date.today().strftime("%W")
    thisweek = Week.thisweek().week
    year = datetime.date.today().strftime("%Y")
    start_date = datetime.datetime.strptime(year + "-W" + str(thisweek) + "-1", "%Y-W%W-%w")
    start_day = start_date.strftime("%b %d, %Y")

    print "isoweek"
    print thisweek
    print "week"
    print week

    set_number = year + week

    user_id = session['user_id']

    # If Collection does not already exist for the current week, create one
    if len(Collection.query.filter(Collection.set_number == set_number,
                                   Collection.user_id == user_id).all()) == 0:

        breakfast_recipes = []
        lunch_recipes = []
        dinner_recipes = []
        user_prefs = []

        breakfast = Category.query.filter(Category.category_name.in_(breakfast_list)).all()
        lunch = Category.query.filter(Category.category_name.in_(lunch_list)).all()
        dinner = Category.query.filter(Category.category_name.in_(dinner_list)).all()

        prefs = db.session.query(UserPreference.category_id).filter(UserPreference.user_id == user_id).all()
        for pref in prefs:
            user_prefs.append(pref[0])

        for category in breakfast:
            for recipe in category.recipe_categories:
                for other_cat in recipe.recipes.recipe_categories:
                    if other_cat.category_id in user_prefs:
                        breakfast_recipes.append(recipe.recipes)

        for category in lunch:
            for recipe in category.recipe_categories:
                for other_cat in recipe.recipes.recipe_categories:
                    if other_cat.category_id in user_prefs:
                        lunch_recipes.append(recipe.recipes)

        for category in dinner:
            for recipe in category.recipe_categories:
                for other_cat in recipe.recipes.recipe_categories:
                    if other_cat.category_id in user_prefs:
                        dinner_recipes.append(recipe.recipes)

        if len(breakfast_recipes) < 5:
            multiply_breakfasts = []
            while len(multiply_breakfasts) < 5:
                for item in breakfast_recipes:
                    multiply_breakfasts.append(item)
            weekly_breakfasts = random.sample(multiply_breakfasts, 5)
        else:
            weekly_breakfasts = random.sample(breakfast_recipes, 5)
        weekly_lunches = random.sample(lunch_recipes, 5)
        weekly_dinners = random.sample(dinner_recipes, 5)

        # Create Collection object from this week's selected breakfast recipes
        day_num = 0

        for item in weekly_breakfasts:
            day_num += 1

            breakfast_recipe = Collection(user_id=session['user_id'],
                                          assigned_date=datetime.date.today(),
                                          set_number=set_number,
                                          set_day=day_num,
                                          meal_type="breakfast",
                                          recipe_id=item.recipe_id)

            db.session.add(breakfast_recipe)

        # Create Collection object from this week's selected lunch recipes
        day_num = 0

        for item in weekly_lunches:
            day_num += 1

            lunch_recipe = Collection(user_id=session['user_id'],
                                      assigned_date=datetime.date.today(),
                                      set_number=set_number,
                                      set_day=day_num,
                                      meal_type="lunch",
                                      recipe_id=item.recipe_id)

            db.session.add(lunch_recipe)

        # Create Collection object from this week's selected dinner recipes
        day_num = 0

        for item in weekly_dinners:
            day_num += 1

            dinner_recipe = Collection(user_id=session['user_id'],
                                       assigned_date=datetime.date.today(),
                                       set_number=set_number,
                                       set_day=day_num,
                                       meal_type="dinner",
                                       recipe_id=item.recipe_id)

            db.session.add(dinner_recipe)

        db.session.commit()

        # Pull this week's Collection objects to pass into the HTML template &
        # render in the meal plan page
        breakfasts = Collection.query.filter(Collection.user_id == user_id,
                                             Collection.set_number == set_number,
                                             Collection.meal_type == "breakfast").order_by(Collection.set_day).all()
        lunches = Collection.query.filter(Collection.user_id == user_id,
                                          Collection.set_number == set_number,
                                          Collection.meal_type == "lunch").order_by(Collection.set_day).all()
        dinners = Collection.query.filter(Collection.user_id == user_id,
                                          Collection.set_number == set_number,
                                          Collection.meal_type == "dinner").order_by(Collection.set_day).all()

        # Get shopping list using Ingredients module
        final_ingredients = ingredients.get_shopping_list(breakfasts, lunches, dinners)

        return render_template("meal_plan.html",
                               now=week,
                               breakfasts=breakfasts,
                               lunches=lunches,
                               dinners=dinners,
                               ingredients=final_ingredients,
                               start_day=start_day)


    # If Collection objects already exist for this week's meal plan, query them
    # and return them with the HTML template
    else:
        breakfasts = Collection.query.filter(Collection.user_id == user_id,
                                             Collection.set_number == set_number,
                                             Collection.meal_type == "breakfast").order_by(Collection.set_day).all()
        lunches = Collection.query.filter(Collection.user_id == user_id,
                                          Collection.set_number == set_number,
                                          Collection.meal_type == "lunch").order_by(Collection.set_day).all()
        dinners = Collection.query.filter(Collection.user_id == user_id,
                                          Collection.set_number == set_number,
                                          Collection.meal_type == "dinner").order_by(Collection.set_day).all()

        # Generate shopping list using Ingredients module
        final_ingredients = ingredients.get_shopping_list(breakfasts, lunches, dinners)

        return render_template("meal_plan.html",
                               now=week,
                               breakfasts=breakfasts,
                               lunches=lunches,
                               dinners=dinners,
                               ingredients=final_ingredients,
                               start_day=start_day)


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


################################################################################
############################# EMAIL SHOPPING LISTS #############################
################################################################################

@app.route("/send", methods=["POST"])
def send_mail():
    user_email = User.query.filter_by(user_id=session['user_id']).first().email

    shopping_contents = dict(request.form)

    msg = Message('Hello',
                  sender=os.environ['MAIL_USERNAME'],
                  recipients=[user_email])
    msg.body = "This is a test email: {}".format(shopping_contents['recipe_name'])
    mail.send(msg)
    return "Sent"

################################################################################
########################### USER PERSONALIZED ROUTES ###########################
################################################################################

@app.route('/profile/<user_id>')
def display_user_profile(user_id):
    """ Displays user's current dietary preferences & profile information (email,
        password, meal plan history) & allows users to update or change """

    user_info = User.query.filter_by(user_id=user_id).first()

    past_plans = {}

    history = Collection.query.filter_by(user_id=user_id).all()

    for recipe in history:
        if recipe.set_number in past_plans:
            past_plans[recipe.set_number].append(recipe)
        else:
            past_plans[recipe.set_number] = [recipe]

    return render_template("preferences.html",
                           user_info=user_info,
                           past_plans=past_plans)


@app.route('/preferences/edit', methods=["POST"])
def edit_user_preferences():
    """ Updates user's dietary preferences """
    # Get info from newly submitted form (plus session user_id)
    user_id = session['user_id']
    prefs_post = dict(request.form)

    # Unpack individual preferences from POST request responses
    new_prefs = []
    for pref in prefs_post['prefs[]']:
        new_prefs.append(pref)

    # Query database to get comparable lists of categories to allow matching of
    # new preferences against old preferences
    new_pref_categories = Category.query.filter(Category.category_name.in_(new_prefs)).all()
    current_prefs = UserPreference.query.filter_by(user_id=user_id).all()
    current_pref_categories = UserPreference.query.filter(UserPreference.user_id == user_id).all()

    #-- Compare old vs. new preferences --#
    # If an preference is in the new list but not in the old, create a new
    # UserPreference object in the database. If a preference is in the old list
    # but not in the new, delete the corresponding UserPreference object from
    # the database
    for item in new_pref_categories:
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

    # Fetch new preferences to return & populate in success function
    updated_pref_ids = db.session.query(UserPreference.category_id).filter_by(user_id=user_id).all()
    updated_pref_names = db.session.query(Category.category_name).filter(Category.category_id.in_(updated_pref_ids)).all()

    # Use jinja to dynamically render html formatting for new prefs & feed
    # html back to template using AJAX call
    return jsonify(render_template('fetched_preferences.html', new_prefs=updated_pref_names))


################################################################################
################################ APP.CONFIG INFO ###############################
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

    # # APP CONFIG SETTINGS FOR FLASK-MAIL
    # app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    # app.config['MAIL_PORT'] = 465
    # app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    # app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    # app.config['MAIL_USE_TLS'] = False
    # app.config['MAIL_USE_SSL'] = True

    app.run(port=5000, host='0.0.0.0')
