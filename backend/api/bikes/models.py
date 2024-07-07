from django.db import models

class BikeStation(models.Model):
    """
    Represents a bike station.

    This model stores information about bike stations including their name, location (latitude and longitude),
    and capacity (number of bike stands available).

    Fields:
        id (int): The primary key of the bike station.
        name (str): The name of the bike station.
        latitude (float): The latitude coordinate of the bike station.
        longitude (float): The longitude coordinate of the bike station.
        capacity (int): The number of bike stands available at the bike station.
    """
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'bike_stations'


class BikeAvailability(models.Model):
    """
    Represents the availability of bikes at a specific time.

    This model stores information about the availability of bikes at a bike station at a specific time.
    It includes details such as the harvest time, last update time, number of available bike stands and bikes,
    and the status.

    Fields:
        id (int): The primary key of the bike availability record.
        harvest_time (datetime): The time when the availability data was harvested.
        last_update_time (datetime): The time when the availability data was last updated.
        station (BikeStation): The bike station to which the availability data belongs.
        available_bike_stands (int): The number of available bike stands at the station.
        available_bikes (int): The number of available bikes at the station.
        status (str): The status of the bike station (e.g., operational, maintenance).
    """
    id = models.AutoField(primary_key=True)
    harvest_time = models.DateTimeField()
    last_update_time = models.DateTimeField()  
    station = models.ForeignKey('BikeStation', on_delete=models.CASCADE)
    available_bike_stands = models.IntegerField()
    available_bikes = models.IntegerField()
    status = models.TextField()

    class Meta:
        managed = True
        db_table = 'bike_availability'


class BikeDistance(models.Model):
    """
    Represents the distance between two bike stations.

    This model stores information about the distance between two bike stations.
    It includes the IDs of the two stations and the distance between them in meters.

    Fields:
        id (int): The primary key of the distance record.
        station_from (BikeStation): The bike station from which the distance is measured.
        station_to (BikeStation): The bike station to which the distance is measured.
        distance (float): The distance between the two stations in meters.
    """
    id = models.IntegerField(primary_key=True)
    station_from = models.ForeignKey(BikeStation, on_delete=models.CASCADE, related_name='distances_from')
    station_to = models.ForeignKey(BikeStation, on_delete=models.CASCADE, related_name='distances_to')
    distance = models.FloatField(help_text="Distance in meters between the two stations")

    class Meta:
        managed = True
        db_table = 'bike_distances'