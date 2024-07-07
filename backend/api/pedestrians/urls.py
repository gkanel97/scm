from django.urls import path
from .views import get_pedestrian_predictions

urlpatterns = [
    path('api/pedestrian/predictions', get_pedestrian_predictions),
]