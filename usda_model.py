""" Models and database functions for the USDA Nutritional Data used in the
ActivEats project """

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.inspection import inspect

db = SQLAlchemy()

################################################################################

class USDA(db.Model):
    """ Table for USDA nutrient data """

    __tablename__ = "usda_info"

    usda_id = db.Column(db.Integer, autoincrement=True, primary_key=True,
                        nullable=False)
    name = db.Column(db.Text, nullable=False)
    ndbno = db.Column(db.Integer, nullable=False)
    serving_grams = db.Column(db.Numeric, nullable=True)  # 'weight' from USDA nutrient report
    serving_string = db.Column(db.Text, nullable=True)  # 'measure'
    cals_per_serving = db.Column(db.Numeric, nullable=True)  # 'value'
    cals_per_100g = db.Column(db.Numeric, nullable=True)  # 'gm'
    sugar_per_serving = db.Column(db.Numeric, nullable=True)
    sugar_per_100g = db.Column(db.Numeric, nullable=True)
    fat_per_serving = db.Column(db.Numeric, nullable=True)
    fat_per_100g = db.Column(db.Numeric, nullable=True)
    carbs_per_serving = db.Column(db.Numeric, nullable=True)
    carbs_per_100g = db.Column(db.Numeric, nullable=True)



################################################################################
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
