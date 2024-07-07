# buses.urls
from django.urls import path
from buses.views import get_bus_display_data, optimize_timetable

urlpatterns = [
    path('api/bus/display', get_bus_display_data, name='get_bus_dispay_data'),
    path('api/bus/timetable', optimize_timetable, name='optimize_timetable')
]