""" Models and database functions for ActivEats project """

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

db = SQLAlchemy()


################################################################################
################################## MAIN TABLES #################################
################################################################################


################################################################################
# RECIPE TABLE

class Recipe(db.Model):
    """ Table for inspecting data directly scraped from Food Network database.

    This data is meant to be for sampling, cleaning & informing data modeling;
    it will not be used in the final product. """

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                          nullable=False)
    recipe_name = db.Column(db.Text, nullable=False)
    recipe_author = db.Column(db.Text, nullable=True)
    servings_num = db.Column(db.Integer, nullable=True)
    servings_unit = db.Column(db.Text, nullable=True)
    text_servings = db.Column(db.Text, nullable=True)
    special_equipment = db.Column(db.Text, nullable=True)
    text_ingredients = db.Column(db.ARRAY(db.Text), nullable=False)
    ingredient_amounts = db.Column(db.JSON, nullable=True)
    ingredient_units = db.Column(db.JSON, nullable=True)
    preparation = db.Column(db.Text, nullable=False)
    total_time = db.Column(db.Interval, nullable=True)
    prep_time = db.Column(db.Interval, nullable=True)
    cook_time = db.Column(db.Interval, nullable=True)
    active_time = db.Column(db.Interval, nullable=True)
    inactive_time = db.Column(db.Interval, nullable=True)
    photo_url = db.Column(db.Text, nullable=True)
    recipe_url = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """ Representative model for recipe items """

        return "<Recipe id={}: {}>".format(self.recipe_id, self.recipe_name)


################################################################################
# INGREDIENT TABLE

class Ingredient(db.Model):
    """ Table for attributes of individual ingredients, including 'whole'
    amounts, with spaces left for nutrient information.

    Has foreign key relationship with a ingredient_amounts middle table (connects
    to recipes table"""

    __tablename__ = "ingredient_attributes"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                              nullable=False)
    ingredient_name = db.Column(db.Text, nullable=False, unique=True)
    whole_grams = db.Column(db.Numeric, nullable=False)
    calories_per_whole = db.Column(db.Numeric, nullable=True)
    carbs_per_whole = db.Column(db.Numeric, nullable=True)
    sugar_per_whole = db.Column(db.Numeric, nullable=True)


    def __repr__(self):
        """ Representative model for ingredients """

        return "<Ingredient id={}: {}>".format(self.ingredient_id,
                                              self.ingredient_name)


################################################################################
# CATEGORY TAGS TABLE

class Category(db.Model):
    """ Table for category groupings for each recipe """

    __tablename__ = "category_tags"

    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                            nullable=False)
    category_name = db.Column(db.Text, nullable=False, unique=True)


    def __repr__(self):
        """ Representative model for categories """

        return "<Category id={}: {}>".format(self.category_id,
                                             self.category_name)


################################################################################
# RECIPE DIFFICULTY TABLE

class Difficulty(db.Model):
    """ Table for difficulty levels of recipe preparation """

    __tablename__ = "difficulty_level"

    difficulty_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                              nullable=False)
    difficulty_level = db.Column(db.Text, nullable=False, unique=True)

    def __repr__(self):
        """ Representative model for difficulty levels """

        return "<Difficulty level: {}>".format(self.difficulty_level)

################################################################################
############################## ASSOCIATION TABLES ##############################
################################################################################

class RecipeIngredient(db.Model):
    """ Middle table connecting recipes with each ingredient they contain;
    links recipes table (Foreign Key: recipe_id) to
    INGREDIENT_ATTRIBUTES table (Foreign Key: ingredient_id) """

    __tablename__ = "recipe_ingredients"

    rec_ing_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                           nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    # recipe_url = db.Column(db.Text, nullable=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient_attributes.ingredient_id'), nullable=False)
    # ingredient_name = db.Column(db.Text, nullable=True)

    recipes = db.relationship("Recipe",
                                           # primaryjoin="recipes.recipe_url==recipe_ingredients.recipe_url",
                                           backref=db.backref("recipe_ingredients",
                                                              order_by=recipe_id))

    ingredient_attribute = db.relationship("Ingredient",
                                           backref=db.backref("recipe_ingredients",
                                                              order_by=ingredient_id))


    def __repr__(self):
        """ Representative model for recipe-ingredient relationships """

        return "<Recipe_id: {}, Ingredient_id:{}>".format(self.recipe_id,
                                                          self.ingredient_id)


class RecipeCategory(db.Model):
    """ Middle table connecting recipes with each category tag that describes
    them; links recipes table (Foreign Key: recipe_id) to
    CATEGORY table (Foreign Key: category_id) """

    __tablename__ = "recipe_categories"

    rec_cat_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                           nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'),
                          nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category_tags.category_id'),
                            nullable=False)

    recipes = db.relationship("Recipe",
                                           backref=db.backref("recipe_categories",
                                                              order_by=recipe_id))

    category_tags = db.relationship("Category",
                                    backref=db.backref("recipe_categories",
                                                       order_by=category_id))

    def __repr__(self):
        """ Representative model for recipe-category relationships """

        return "Recipe_id: {}, Category_id:{}>".format(self.recipe_id,
                                                       self.category_id)


class RecipeDifficulty(db.Model):
    """ Middle table connecting recipes with their respective difficulty level;
    links recipes table (Foreign Key: recipe_id) to DIFFICULTY
    table (Foreign Key: difficulty_id) """

    __tablename__ = "recipe_difficulty"

    rec_dif_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'),
                          nullable=False)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('difficulty_level.difficulty_id'),
                              nullable=False)

    recipes = db.relationship("Recipe",
                                           backref=db.backref("recipe_difficulty",
                                                              order_by=recipe_id))

    category_tags = db.relationship("Difficulty",
                                    backref=db.backref("recipe_difficulty",
                                                       order_by=difficulty_id))

    def __repr__(self):
        """ Representative model for recipe-difficulty relationships """

        return "<Recipe_id: {}, Difficulty_id: {}>".format(self.recipe_id,
                                                           self.difficulty_id)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipe_data'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."