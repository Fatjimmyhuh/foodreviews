import sys, os 
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FoodReviews.settings")

import django
django.setup()

from reviews.models import Restaurant 


def save_Restaurant_from_row(restaurant_row):
    restaurant = Restaurant()
    restaurant.id = restaurant_row[0]
    restaurant.name = restaurant_row[1]
    restaurant.save()
    
    
if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        print ("Reading from file " + str(sys.argv[1]))
        restaurants_df = pd.read_csv(sys.argv[1])
        print (restaurants_df)

        restaurants_df.apply(
            save_Restaurant_from_row,
            axis=1
        )

        print ("There are {} restaurants".format(Restaurant.objects.count()))
        
    else:
        print ("Please, provide restaurant file path")
