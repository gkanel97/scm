import requests
from datetime import datetime
from models.ExternalApiHandler import ExternalApiHandler
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

class BusApiHandler(ExternalApiHandler):

    def __init__(self) -> None:
        self.data_endpoint = 'https://api.nationaltransport.ie/gtfsr/v2/gtfsr'
        self.data_endpoint_bus = "https://api.nationaltransport.ie/gtfsr/v2/Vehicles"
        self.api_key = ''
        self.headers = {'format': 'json'}

    def get_trips_table_schema(self) -> StructType:
        bus_trips_schema = StructType([
            StructField("trip_id", StringType(), True),
            StructField("start_datetime", TimestampType(), True),
            StructField("schedule_relationship", StringType(), True),
            StructField("route_id", StringType(), True),
            StructField("direction_id", IntegerType(), True),
            StructField("vihecle", StringType(), True),
            StructField("delay", DoubleType(), True)
        ])
        return bus_trips_schema
    
    def get_positions_table_schema(self) -> StructType:
        bus_positions_schema = StructType([
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("trip_id", StringType(), True)
        ])
        return bus_positions_schema
    
    def get_table_create_queries(self):
        trips_create_table_query = """
            CREATE TABLE IF NOT EXISTS bus_trips (
                trip_id VARCHAR(255),
                start_datetime TIMESTAMP,
                schedule_relationship VARCHAR(255),
                route_id VARCHAR(255),
                direction_id INTEGER,
                vihecle VARCHAR(255),
                delay REAL
            )
            """
        position_create_table_query = """
            CREATE TABLE IF NOT EXISTS bus_positions (
                latitude REAL,
                longitude REAL,
                timestamp TIMESTAMP,
                trip_id VARCHAR(255)
            )
            """
        return [trips_create_table_query, position_create_table_query]

    def fetch(self) -> dict:
        resp = requests.get(self.data_endpoint, params={'format': 'json'}, headers={'x-api-key': self.api_key})
        route_data = resp.json()
        resp_bus = requests.get(self.data_endpoint_bus, params={'format': 'json'}, headers={'x-api-key': self.api_key})
        bus_data = resp_bus.json()
        trip_arr = []
        position_arr = []

        # Extract trip and position data for all buses
        
        for vehicle_data in route_data['entity']:
            # Copy trip data, convert start date and time to datetime and remove strings
            # trip = vehicle_data['vehicle']['trip'].copy()
            trip = vehicle_data['trip_update']['trip'].copy()
            trip['start_datetime'] = datetime.strptime(
                f'{trip["start_date"]} {trip["start_time"]}',
                '%Y%m%d %H:%M:%S'
            )
            trip.pop('start_date')
            trip.pop('start_time')
            # trip['vehicle'] = vehicle_data['trip_update']['vehicle']['id']
            delays=[]
            if 'stop_time_update' in vehicle_data['trip_update']:
                for item in vehicle_data['trip_update']['stop_time_update']:
                    # Initialize a variable to store the delay for this item
                    delay = 0  # Default value if no delay information is found
                    
                    # Check for 'arrival' delay, if it exists
                    if 'arrival' in item and 'delay' in item['arrival']:
                        delay = item['arrival']['delay']
                    # If no 'arrival' delay, check for 'departure' delay
                    elif 'departure' in item and 'delay' in item['departure']:
                        delay = item['departure']['delay']
                    
                    # Append the found delay to the list, or 0 if neither is found
                    delays.append(delay)
            else:
                delays.append(0)
            if delays:
                trip['delay'] = sum(delays) / len(delays)
            else:
                trip['delay'] = 0
            if(len(trip) != 6):
                continue
            else:
                trip['vihecle']=0
                trip_arr.append(trip)
            
            
        for vehicle_data in bus_data['entity']:
            # Extract position data and add to position array
            position = vehicle_data['vehicle']['position'].copy()
            if position['longitude'] != 0 and position['latitude'] != 0:
                position['timestamp'] = datetime.fromtimestamp(int(vehicle_data['vehicle']['timestamp']))
                position['trip_id'] = vehicle_data['vehicle']['trip']['trip_id']
                position_arr.append(position)
        return dict(positions=position_arr, trips=trip_arr)
    
    def generate_spark_dataframes(self, spark_session) -> dict:
        data = self.fetch()
        trip_df = spark_session.createDataFrame(data['trips'], schema=self.get_trips_table_schema())
        position_df = spark_session.createDataFrame(data['positions'], schema=self.get_positions_table_schema())
        return [
            { 'table_name': 'bus_trips', 'spark_df': trip_df }, 
            { 'table_name': 'bus_positions', 'spark_df':  position_df }
        ]