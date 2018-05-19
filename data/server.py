""" Recipes """

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Recipe
import pdb

app = Flask(__name__)

app.secret_key = "ITS_A_SECRET"

################################################################################
# ROUTES GO HERE



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
