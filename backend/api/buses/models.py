from django.db import models
import pandas as pd
import os
import json
from django.conf import settings

class BusTrip(models.Model):
    """
    Represents a bus trip.

    This model stores information about a bus trip including its ID, start datetime,
    schedule relationship, route ID, direction ID, vehicle, and delay.

    Attributes:
        trip_id (str): The ID of the bus trip.
        start_datetime (datetime): The start datetime of the bus trip.
        schedule_relationship (str): The schedule relationship of the bus trip.
        route_id (str): The ID of the route for the bus trip.
        direction_id (int): The direction ID of the bus trip.
        vehicle (str): The vehicle associated with the bus trip.
        delay (float): The delay of the bus trip.
    """
    trip_id = models.TextField()
    start_datetime = models.DateTimeField()
    schedule_relationship = models.TextField()
    route_id = models.TextField()
    direction_id = models.IntegerField()
    vihecle = models.TextField()
    delay = models.FloatField()

    class Meta:
        managed = False
        db_table = 'bus_trips'


class BusRouteShape(models.Model):
    """
    Represents the shape of a bus route.

    This model stores information about the shape of a bus route including the route short name,
    route ID, shape ID, latitude, longitude, and sequence.

    Attributes:
        route_short_name (str): The short name of the bus route.
        route_id (str): The ID of the bus route.
        shape_id (str): The ID of the shape of the bus route.
        latitude (float): The latitude coordinate of the shape point.
        longitude (float): The longitude coordinate of the shape point.
        sequence (int): The sequence number of the shape point.
    """
    route_short_name = models.TextField()
    route_id = models.TextField()
    shape_id = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    sequence = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'bus_routes'


class BusPositions(models.Model):
    """
    Represents the position of a bus.

    This model stores information about the position of a bus including the trip ID,
    timestamp, latitude, and longitude.

    Attributes:
        trip_id (str): The ID of the bus trip.
        timestamp (datetime): The timestamp of the position.
        latitude (float): The latitude coordinate of the bus position.
        longitude (float): The longitude coordinate of the bus position.
    """
    trip_id = models.TextField()
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        managed = False
        db_table = 'bus_positions'

def fetch_and_process_data():
    """
    Fetches and processes bus data. Reads bus data from a JSON file located at "buses/data/data.json" and a CSV file located at "buses/data/routes1.txt".

    :return: A tuple containing the bus data (as a dictionary) and the routes DataFrame.
    :rtype: tuple
    """
    #json_file_path = os.path.join(settings.BASE_DIR, 'buses', 'data', 'data.json')
    with open("buses/data/data.json", 'r') as json_file:
        data = json.load(json_file)
    #print(data)
    #routes_csv_path = os.path.join(settings.BASE_DIR, 'buses', 'data', 'routes.txt')
    routes_df = pd.read_csv("buses/data/routes1.txt")
    #print(routes_df.head())
    return data, routes_df
