import numpy as np
import pandas as pd
from .models import BusRouteShape, BusTrip

class BusDelayMonitor():

    def __init__(self, start_time, end_time):
        """
        Initializes an instance of the class with specified start and end times. This constructor 
        sets up the basic configuration needed to perform subsequent calculations or operations 
        related to time intervals.

        :param start_time: The starting time for the interval.
        :type start_time: datetime
        :param end_time: The ending time for the interval.
        :type end_time: datetime

        Additionally, this method initializes an empty list to store delay quartiles, which could be
        used later to analyze delays within the specified time interval.
        
        The instance variables initialized are:
        - self.start_time: stores the starting time.
        - self.end_time: stores the ending time.
        - self.delay_quartiles: an empty list to hold quartile data related to delays.
        """
        self.start_time = start_time
        self.end_time = end_time
        self.delay_quartiles = []

    def get_trips_df(self):
        """
        Retrieves and returns a DataFrame containing data on bus trips that occurred within the specified 
        start and end times of this instance. The method queries the database for trips based on the 
        time range and extracts relevant details to construct a DataFrame.

        The extracted fields include:
        - 'trip_id': Identifier for the bus trip.
        - 'start_datetime': Start time of the trip.
        - 'schedule_relationship': Describes the timeliness of the trip (e.g., scheduled, delayed).
        - 'route_id': Identifier for the route taken by the trip.
        - 'direction_id': Direction of the trip (e.g., outbound, return).
        - 'delay': Recorded delay in minutes.

        :returns: A pandas DataFrame containing the details of the bus trips within the specified time range.
        :rtype: pandas.DataFrame

        This method is typically used to perform analysis on trip data, such as delay analysis, frequency of trips,
        or compliance with schedules.
        """
        trips = BusTrip.objects.filter(start_datetime__range=(self.start_time, self.end_time))
        trips_df = pd.DataFrame(
            list(
                trips.values(
                    'trip_id', 
                    'start_datetime', 
                    'schedule_relationship', 
                    'route_id', 
                    'direction_id',
                    'delay'
                )
            )
        )
        return trips_df
    
    def calculate_delays(self):
        """
        Calculates and returns a DataFrame containing the average delay and classifications of delays for bus routes
        within the specified time range. This method combines trip data with route names to provide a clear understanding
        of delay patterns on different routes.

        The method performs the following steps:
        - Retrieves trip data including delays for the specified interval using `get_trips_df`.
        - Retrieves route names using `get_route_names`.
        - Extracts delays into a numpy array.
        - Calculates delay quartiles and applies classifications to each delay.
        - Computes the average delay for each route and merges this with the route names to enhance readability.

        :returns: A DataFrame that includes route names, route IDs, and their corresponding average delays and delay classifications.
        :rtype: pandas.DataFrame

        The returned DataFrame columns include:
        - 'route_id': Identifier for the bus route.
        - 'name': Name of the bus route.
        - 'delay': Average delay recorded for the route.

        This DataFrame can be used to assess the performance of bus routes in terms of punctuality and to identify
        routes that frequently experience significant delays.
        """
        # Get trips and bus name dataframes
        trips_df = self.get_trips_df()
        names_df = self.get_route_names()

        if trips_df.empty or names_df.empty:
            return pd.DataFrame()

        # Extract the delays in a numpy array
        delay_arr = np.array(trips_df['delay'].values)

        # Calculate the delay quartiles and classify the delays
        self.calculate_delay_quartiles(delay_arr)
        trips_df['delay_class'] = trips_df['delay'].apply(self.classify_delays)

        # Get the classes into the separate columns
        # delay_df = trips_df.pivot_table(index='route_id', columns='delay_class', aggfunc=len, fill_value=0)
        delay_df = trips_df.groupby(['route_id', 'delay_class']).size().unstack(fill_value=0)

        # Merge the route names
        delay_df = delay_df.merge(names_df, on='route_id', how='left')

        # Remove NaN values
        delay_df = delay_df.dropna()

        return delay_df

    def get_route_names(self):
        """
        Fetches and indexes the most current route names for bus routes from the BusRouteShape table, 
        based on the highest sequence number for each route.

        Processes:
        - Query and sort all entries from the BusRouteShape table by 'sequence' descending.
        - Remove duplicate 'route_id' entries, retaining the entry with the highest sequence.
        - Return a DataFrame indexed by 'route_id' with the 'route_short_name'.

        :returns: DataFrame with columns ['route_id', 'route_short_name'], indexed by 'route_id'.
        :rtype: pandas.DataFrame
        """
        # Get the rows from the BusRouteShape table
        # For every route_id keep the row with the highest sequence number
        routes = BusRouteShape.objects.all()
        routes_df = pd.DataFrame(list(routes.values()))
        routes_df = routes_df.sort_values('sequence', ascending=False)
        routes_df = routes_df.drop_duplicates('route_id')
        return routes_df[['route_id', 'route_short_name']].set_index('route_id')
    
    def calculate_delay_quartiles(self, delay_arr):
        """
        Calculates the 33rd and 66th percentiles of bus delay times and stores them in an instance variable.
        Only non-negative delays are considered for calculation to ensure the analysis reflects actual delays.
        """
        delay_arr = delay_arr[delay_arr >= 0]  
        if delay_arr.size > 0:
            self.delay_quartiles = np.percentile(delay_arr, [33, 66])
        else:
            self.delay_quartiles = np.array([])  


    
    def classify_delays(self, delay):
        """
        Classifies bus delays into categories based on predefined quartile values stored in `self.delay_quartiles`.
        This method categorizes delays as 'Early', 'On time', 'Short delay', 'Medium delay', or 'Long delay'.

        :param delay: The delay time of a bus trip to be classified.
        :type delay: int or float

        :returns: A string representing the category of the delay.
        :rtype: str
        """
        if delay < 0:
            return 'Early'
        elif delay == 0:
            return 'On time'
        if self.delay_quartiles.size == 0: 
            return None 
        if delay < self.delay_quartiles[0]:
            return 'Short delay'
        elif delay < self.delay_quartiles[1]:
            return 'Medium delay'
        else:
            return 'Long delay'

