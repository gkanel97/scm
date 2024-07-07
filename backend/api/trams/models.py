from django.db import models

class TramStop(models.Model):
    """
    Represents a tram stop.

    Fields:
        id (int): The unique identifier of the tram stop.
        code (str): The code associated with the tram stop.
        name (str): The name of the tram stop.
        latitude (float): The latitude coordinate of the tram stop.
        longitude (float): The longitude coordinate of the tram stop.
        line (str): The tram line associated with the tram stop.
    """
    id = models.IntegerField(primary_key=True)
    code = models.TextField()
    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    line = models.TextField()

    class Meta:
        managed = True
        db_table = 'tram_stops'

class TramArrivals(models.Model):
    """
    Represents tram arrivals at a tram stop.

    Fields:
        arrival_time (datetime): The arrival time of the tram.
        stop_id (str): The ID of the tram stop.
        batch_id (int): The batch ID associated with the arrival.
        direction (str): The direction of the tram.
        destination (str): The destination of the tram.
        status (str): The status of the tram arrival.
    """
    arrival_time = models.DateTimeField()
    stop_id = models.TextField()
    batch_id = models.IntegerField()
    direction = models.TextField()
    destination = models.TextField()
    status = models.TextField()
 

    class Meta:
        managed = True
        db_table = 'tram_arrivals'
