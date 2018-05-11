""" Models and database functions for ActivEats project """

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

################################################################################
# MODEL DEFINITIONS

class SampleFNRecipe(db.Model):
    """ Table for inspecting data directly scraped from Food Network database.

    This data is meant to be for sampling, cleaning & informing data modeling;
    it will not be used in the final product. """

    __tablename__ = "food_network_inspect"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_name = db.Column(db.String(1000), nullable=False)
    recipe_author = db.Column(db.String(1000), nullable=True)
    category_tags = db.Column(db.String(1000), nullable=False)
    difficulty = db.Column(db.String(500), nullable=True)
    servings = db.Column(db.String(500), nullable=False)
    special_equipment = db.Column(db.String(500), nullable=True)
    ingredients = db.Column(db.String(5000), nullable=False)
    preparation = db.Column(db.String(10000), nullable=False)
    total_time = db.Column(db.String(100), nullable=False)
    prep_time = db.Column(db.String(100), nullable=True)
    cook_time = db.Column(db.String(100), nullable=True)
    active_time = db.Column(db.String(100), nullable=True)
    inactive_time = db.Column(db.String(100), nullable=True)
    photo_url = db.Column(db.String(1000), nullable=True)
    recipe_url = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        """ Representative model for recipe items """

        return "<Recipe id={}: {}>".format(self.recipe_id, self.recipe_name)




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