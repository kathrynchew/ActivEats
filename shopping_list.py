# File to hold functions that generate shopping lists for ActivEats
from model import (connect_to_db, db, Recipe, Ingredient, RecipeIngredient,
                   Category, RecipeCategory, Difficulty, RecipeDifficulty,
                   User, UserPreference, Collection)
from data_cleaning_sets import breakfast_list, lunch_list, dinner_list
from flask import Flask, render_template, redirect, request, flash, session, jsonify

app = Flask(__name__)

app.secret_key = "ITS_A_SECRET"

################################################################################

def fetch_ingredients(recipe):
    """ Unpacks ingredient names, amounts, units for an individual recipe """

    for key, value in recipe.ingredient_amounts.items():
        print key, value


def this_recipe():

    recipe = Recipe.query.filter_by(recipe_id=700).first()

    fetch_ingredients(recipe)

this_recipe

