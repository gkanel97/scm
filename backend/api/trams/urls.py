from django.urls import path

from .views import get_tram_display_data, get_predictions

urlpatterns = [
    path('api/tram/display', get_tram_display_data, name='get_tram_display_data'),
    path('api/tram/predictions',  get_predictions, name='get_predictions')
]