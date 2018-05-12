""" Models and database functions for ActivEats project """

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

db = SQLAlchemy()

################################################################################
# MODEL DEFINITIONS

class SampleFNRecipe(db.Model):
    """ Table for inspecting data directly scraped from Food Network database.

    This data is meant to be for sampling, cleaning & informing data modeling;
    it will not be used in the final product. """

    __tablename__ = "food_network_inspect"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True, 
                          nullable=False)
    recipe_name = db.Column(db.Text, nullable=False)
    recipe_author = db.Column(db.Text, nullable=True)
    category_tags = db.Column(db.ARRAY(db.Text), nullable=False)
    difficulty = db.Column(db.Text, nullable=True)
    servings = db.Column(db.Text, nullable=False)
    special_equipment = db.Column(db.Text, nullable=True)
    text_ingredients = db.Column(db.ARRAY(db.Text), nullable=False)
    ingredients_names = db.Column(db.ARRAY(db.Text), nullable=False)
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


class Ingredient(db.Model):
    """ Table for attributes of individual ingredients, including 'whole'
    amounts, with spaces left for nutrient information.

    Has foreign key relationship with a ingredient_amounts middle table (connects
    to food_network_inspect table"""

    __tablename__ = "ingredient_attributes"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                              nullable=False)
    ingredient_name = db.Column(db.Text, nullable=False)
    whole_grams = db.Column(db.Numeric, nullable=False)
    calories_per_whole = db.Column(db.Numeric, nullable=True)
    carbs_per_whole = db.Column(db.Numeric, nullable=True)
    sugar_per_whole = db.Column(db.Numeric, nullable=True)


    def __repr__(self):
        """ Representative model for ingredients """

        return "<Ingredient id={}: {}".format(self.ingredient_id, 
                                              self.ingredient_name)




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