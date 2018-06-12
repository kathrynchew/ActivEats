from usda_model import USDA, connect_to_db, db
from server import app


def load_usda():
    """ Load USDA data into USDA_INFO table """

    with open('test_usda_api/usda_all.txt', 'r') as data:
        usda_data = eval(data.read())

    print "Loading USDA Nutrition Facts"

    for key, value in usda_data.items():

        inner = usda_data[key]['report']['foods']

        for food in inner:
            name = food['name']
            ndbno = food['ndbno']
            serving_grams = food['weight']
            serving_string = food['measure']

            for nutrient in food['nutrients']:
                if nutrient['nutrient_id'] == "208":

                    if nutrient['value'] == '--':
                        cals_per_serving = None
                    else:
                        cals_per_serving = nutrient['value']

                    if nutrient['gm'] == '--':
                        cals_per_100g = None
                    else:
                        cals_per_100g = nutrient['gm']

                elif nutrient['nutrient_id'] == "269":

                    if nutrient['value'] == '--':
                        sugar_per_serving = None
                    else:
                        sugar_per_serving = nutrient['value']

                    if nutrient['gm'] == '--':
                        sugar_per_100g = None
                    else:
                        sugar_per_100g = nutrient['gm']

                elif nutrient['nutrient_id'] == "204":

                    if nutrient['value'] == '--':
                        fat_per_serving = None
                    else:
                        fat_per_serving = nutrient['value']

                    if nutrient['gm'] == '--':
                        fat_per_100g = None
                    else:
                        fat_per_100g = nutrient['gm']

                elif nutrient['nutrient_id'] == "205":

                    if nutrient['value'] == '--':
                        carbs_per_serving = None
                    else:
                        carbs_per_serving = nutrient['value']

                    if nutrient['gm'] == '--':
                        carbs_per_100g = None
                    else:
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