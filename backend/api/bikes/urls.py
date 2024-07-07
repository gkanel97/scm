from django.urls import path
from .views import get_bike_display_data, get_bike_recommendations, get_bike_predictions

urlpatterns = [
    path('api/bikes/display/', get_bike_display_data, name='get_bike_display_data'),
    path('api/bikes/recommendations/', get_bike_recommendations, name='get_bike_recommendations'),
    path('api/bikes/predictions', get_bike_predictions, name='get_bike_predictions')
]
