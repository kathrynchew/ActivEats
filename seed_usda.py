from usda_model import USDA, connect_to_db, db
from server import app
import json


def load_usda():
    """ Load USDA data into USDA_INFO table """

    with open('test_usda_api/usda_all.txt', 'r') as data:
        usda_data = eval(data.read())

    for value in usda_data.values():
        for report in value:
            for food in report['foods']:
                name = food['name']
                ndbno = food['ndbno']
                serving_grams = food['weight']
                serving_string = food['measure']

                for nutrient in food['nutrients']:
                    if nutrient['nutrient_id'] == "208":
                        cals_per_serving = nutrient['value']
                        cals_per_100g = nutrient['gm']
                    elif nutrient['nutrient_id'] == "269":
                        sugar_per_serving = nutrient['value']
                        sugar_per_100g = nutrient['gm']
                    elif nutrient['nutrient_id'] == "204":
                        fat_per_serving = nutrient['value']
                        fat_per_100g = nutrient['gm']
                    elif nutrient['nutrient_id'] == "205":
                        carbs_per_serving = nutrient['value']
                        carbs_per_100g = nutrient['gm']

                usda_object = USDA(name=name,
                                   ndbno=ndbno,
                                   serving_grams=serving_grams,
                                   serving_string=serving_string,
                                   cals_per_serving=cals_per_serving,
                                   cals_per_100g=cals_per_100g,
                                   sugar_per_serving=sugar_per_serving,
                                   sugar_per_100g=sugar_per_100g,
                                   fat_per_serving=fat_per_serving,
                                   fat_per_100g=fat_per_100g,
                                   carbs_per_serving=carbs_per_serving,
                                   carbs_per_100g=carbs_per_100g)

                db.session.add(usda_object)

    db.session.commit()


################################################################################
if __name__ == "__main__":
    connect_to_db(app)

    db.create_all()

    load_usda()