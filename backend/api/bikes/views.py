import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import BikeDistance
from .models import BikeStation, BikeAvailability
from .recommender import BikeRecommender

def get_latest_bike_availability():
    """
    Retrieves the latest bike availability data for each bike station from a database using Django ORM. 
    This function performs a subquery for each station to find the most recent availability update and then 
    annotates the main query of bike stations with this data. It ensures that all stations are listed with 
    their most recent availability of bikes and bike stands, including handling cases where recent data might be null.

    The function constructs a queryset that:
    - Executes a subquery for the latest update time, available bikes, and bike stands per station.
    - Annotates the results with these details, ensuring every station record is updated with its latest figures.
    - Uses Coalesce to handle null values, ensuring fields without data receive a default value (0 for bikes and stands, None for time).
    
    :returns: A list of dictionaries, each containing the station's id, name, latitude, longitude, capacity,
              and latest availability data including the last update time, number of available bikes, and bike stands.
    :rtype: list

    This method provides essential data for real-time applications requiring up-to-date information on bike station statuses.
    """
    most_recent_availability_subquery = BikeAvailability.objects.filter(
        station=OuterRef('pk')
    ).order_by('-last_update_time').values('last_update_time', 'available_bikes', 'available_bike_stands')[:1]

    stations_with_recent_data = BikeStation.objects.annotate(
        last_update_time=Subquery(most_recent_availability_subquery.values('last_update_time')[:1]),
        available_bikes=Subquery(most_recent_availability_subquery.values('available_bikes')[:1]),
        available_bike_stands=Subquery(most_recent_availability_subquery.values('available_bike_stands')[:1])
    ).values('id', 'name', 'latitude', 'longitude', 'capacity').order_by('id')

    # Use Coalesce for null values
    stations_with_recent_data = stations_with_recent_data.annotate(
        last_update_time=Coalesce('last_update_time', None),  
        available_bikes=Coalesce('available_bikes', 0),
        available_bike_stands=Coalesce('available_bike_stands', 0)  
    )
    return list(stations_with_recent_data)


def load_prophet_models(prophet_models_file):
    """
    Loads and returns serialized Prophet forecasting models from a specified file. If the file exists, 
    it reads and deserializes the models using Python's pickle module. If the file does not exist, the 
    function prints an error message and returns None.

    :param prophet_models_file: The path to the file containing the serialized Prophet models.
    :type prophet_models_file: str

    :returns: The loaded Prophet models if the file exists, otherwise None.
    :rtype: dict or None

    This function is useful for applications that need to load pre-trained Prophet models for time series 
    forecasting without needing to retrain models from scratch, thereby saving computation time and resources.
    """    
    if os.path.exists(prophet_models_file):
        with open(prophet_models_file, 'rb') as f:
            loaded_models = pickle.load(f)
        return loaded_models
    else:
        print(f"Prophet models file '{prophet_models_file}' not found.")
        return None

@csrf_exempt
@require_GET
@cache_page(60 * 5)    
def get_bike_display_data(request):
    """
    Fetch and return the latest bike station availability data. This Django view handles GET requests
    and responds with a JSON object that contains current data about the availability of bikes at various stations.
    The response includes each station's ID, name, location, capacity, and current number of available bikes and bike stands.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: JsonResponse containing bike station data formatted as:
             {
                'bike_station_data': [
                    {'id': int, 'name': str, 'latitude': float, 'longitude': float,
                     'capacity': int, 'available_bikes': int, 'available_bike_stands': int,
                     'last_update_time': datetime}
                ]
             }
    :rtype: JsonResponse
    """
    station_data = get_latest_bike_availability()
    return JsonResponse({ 'bike_station_data': station_data }, status=200)
    
@csrf_exempt
@require_GET
# @cache_page(60 * 5)
def get_bike_recommendations(request):
    """
    A Django view function to fetch and respond with bike movement recommendations based on current bike availability, 
    bike station distances, and forecasted bike usage. This function is exposed as an API endpoint that handles GET requests 
    and returns JSON data containing the recommended movements of bikes to optimize their distribution across stations.

    The function performs several steps:
    - Fetches the most recent bike availability data.
    - Retrieves distance data between bike stations.
    - Defines a future timestamp range for which bike usage is to be predicted.
    - Loads serialized Prophet forecasting models for predicting bike usage.
    - Initializes a bike recommender system with the fetched data and models.
    - Generates and returns bike movement recommendations based on current and forecasted data.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :returns: A JsonResponse object containing the bike recommendations in a JSON format with a 200 HTTP status.
    :rtype: JsonResponse

    This endpoint is useful for client-side applications that require real-time recommendations for bike redistributions 
    to ensure optimal availability across a network of bike stations.
    """
    # Fetch the most recent bike availability data
    bike_availability = get_latest_bike_availability()
    bike_availability_df = pd.DataFrame(bike_availability)

    # Fetch the bike station distances
    bike_distances = BikeDistance.objects.all().values('station_from', 'station_to', 'distance')
    bike_distances_df = pd.DataFrame(bike_distances)

    # Define timestamps used for predictions
    prediction_time = datetime.now() + timedelta(hours=1)
    timestamps_to_predict = pd.date_range(prediction_time, periods=10, freq='1H')
    timestamps_to_predict = pd.DataFrame(timestamps_to_predict, columns=['ds'])

    # Load the forecasting model
    prophet_models_file = 'bikes/analytics/bike_model.pkl'
    prophet_model = load_prophet_models(prophet_models_file)

    # Initialize the bike recommender
    bike_recommender = BikeRecommender(
        stations_df=bike_availability_df,
        distances_df=bike_distances_df,
        forecast_model=prophet_model,
        timestamps_to_predict=timestamps_to_predict
    )
    recommendations = bike_recommender.generate_recommendations()

    # Get bike station names and ids from BikeStation model
    bike_stations = BikeStation.objects.values('id', 'name')
    bike_stations_dict = { station['id']: station['name'] for station in bike_stations }

    return JsonResponse({ 'bike_recommendations': recommendations, 'bike_stations': bike_stations_dict }, status=200)

@csrf_exempt
@require_POST
# @cache_page(60 * 5)
def get_bike_predictions(request):
    """
    Handles POST requests to predict the availability of bikes at various stations after a specified number of hours.
    The endpoint requires a JSON body with a `forecast_timedelta` indicating the number of hours into the future to predict.
    This function loads pre-trained Prophet models for each station, uses them to predict bike availability, and returns the predictions.

    :param request: The HTTP request object containing the forecast timedelta.
    :type request: HttpRequest

    :return: JsonResponse containing predictions for each bike station, formatted as:
             {
                'bike_predictions': [
                    {'id': int, 'name': str, 'latitude': float, 'longitude': float,
                     'capacity': int, 'prediction': int}
                ]
             }
    :rtype: JsonResponse

    The function retrieves the forecast time from the request, loads forecasting models, and computes predictions for
    each station using the specified forecast timestamp. The results include the station's ID, name, location, capacity,
    and the predicted number of available bikes.
    """
    # Retrieve forecast time from request
    request_data = json.loads(request.body)
    forecast_timedelta = int(request_data.get('forecast_timedelta', 0))

    # Load the forecasting model
    prophet_models_file = 'bikes/analytics/bike_model.pkl'
    prophet_models = load_prophet_models(prophet_models_file)

    # Retrieve bike station id, name, latitude, and longitude
    bike_stations = BikeStation.objects.values('id', 'name', 'latitude', 'longitude', 'capacity')

    # Forecast the requested bike availability
    predictions = []
    forecast_timestamp = datetime.now() + timedelta(hours=forecast_timedelta)
    
    for station in bike_stations:
        station_id = station['id']
        station_model = prophet_models[station_id]
        station_pred = station_model.predict(pd.DataFrame({ 'ds': [forecast_timestamp] }))
        pred_value = round(max(0, station_pred.yhat.values[0]))
        predictions.append({ 
            'id': station_id,
            'name': station['name'],
            'longitude': station['longitude'],
            'latitude': station['latitude'],
            'capacity': station['capacity'],
            'prediction': pred_value
        })

    return JsonResponse({ 'bike_predictions': predictions }, status=200)