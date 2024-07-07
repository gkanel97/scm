import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class BikeRecommender:

    def __init__(self, stations_df, distances_df, forecast_model, timestamps_to_predict):
        """
        Initializes a BikeRecommender instance for managing and optimizing bike distribution 
        across stations based on forecasts and distances between stations.

        :param stations_df: DataFrame containing data about each bike station, such as station ID,
                            available bikes, and available bike stands.
        :type stations_df: pandas.DataFrame
        :param distances_df: DataFrame containing distance data between each pair of bike stations.
        :type distances_df: pandas.DataFrame
        :param forecast_model: A model or a dictionary of models used for predicting future bike
                               availability at each station.
        :type forecast_model: dict or any forecast model
        :param timestamps_to_predict: List of timestamps for which bike availability predictions
                                      are required.
        :type timestamps_to_predict: list of datetime
        """
    
        self.stations_df = stations_df
        self.distances_df = distances_df
        self.forecast_model = forecast_model
        self.timestamps_to_predict = timestamps_to_predict
        self._critical_threshold = 3
        self._critical_probability = 0.5
        self._surplus_probability = 0.35
        self._maximum_moves = 20


    def calculate_run_out_probability(self, station_id, bike_moves, forecast=None):
        """
        Calculate the probability that a bike station will run out of bikes based on current forecasts,
        bike movements, and critical thresholds. Adjusts for stations already empty to ensure 
        accurate risk assessment.

        :param station_id: Identifier for the bike station
        :type station_id: int
        :param bike_moves: Number of bikes added or removed from the station (negative for removals)
        :type bike_moves: int
        :param forecast: Optional forecast data for calculating the probability. Uses internal model if None.
        :type forecast: Forecast object, optional
        
        :returns: The probability of the station running out of bikes.
        :rtype: float
        """

        forecast = self.forecast_model[station_id].predict(self.timestamps_to_predict) if forecast is None else forecast
        uncertainty_range = forecast.yhat_upper - forecast.yhat_lower

        # Check if uncertainty_range is a pandas Series and if it contains zero.
        if isinstance(uncertainty_range, pd.Series):
            if (uncertainty_range == 0).any():
                uncertainty_range += 1  # Avoid division by zero
        else:
            # If it's not a Series, directly check if it's zero.
            if uncertainty_range == 0:
                uncertainty_range = 1

        proximity = (forecast.yhat + bike_moves - self._critical_threshold) / uncertainty_range
        valid_prox = [prox for prox in proximity if not np.isnan(prox)]
        if not valid_prox:
            run_out_prob = 1.0 if bike_moves < 0 else 0.0
        else:
            run_out_prob = np.mean([max(0, 1 - abs(prox)) for prox in valid_prox])

        # Ensure high probability of running out if there are no available bikes
        if self.stations_df[self.stations_df['id'] == station_id]['available_bikes'].values[0] == 0:
            run_out_prob = 1.0

        return run_out_prob


    def calculate_bike_surplus(self, station_id, available_bikes, run_out_prob):
        """
        Calculate the surplus of bikes at a given station, considering a threshold for surplus and the probability of running out of bikes. The function decrements the count of available bikes until the station either falls below the critical threshold or the run out probability reaches the surplus threshold. The surplus is computed as the number of bikes above the critical threshold that can be removed without significantly increasing the risk of running out.

        :param station_id: Identifier for the bike station
        :type station_id: int
        :param available_bikes: The current number of bikes available at the station
        :type available_bikes: int
        :param run_out_prob: The initial probability of the station running out of bikes
        :type run_out_prob: float

        :returns: The calculated number of surplus bikes that can be safely removed from the station.
        :rtype: int

        The function iteratively checks the available bikes against the critical threshold and adjusts the count based on updated run out probabilities with each bike removed. The goal is to maximize the number of bikes that can be redistributed while maintaining a low risk of the station running empty.
        """
        forecast = self.forecast_model[station_id].predict(self.timestamps_to_predict)
        bike_surplus = 0
        while available_bikes > self._critical_threshold and run_out_prob < self._surplus_probability:
            available_bikes -= 1
            bike_surplus += 1
            run_out_prob = self.calculate_run_out_probability(station_id, -bike_surplus, forecast)
        return bike_surplus

    
    def get_station_distances(self, station_id):
        """
        Retrieves the distances from a specified station to all other stations, including a minimal 
        distance to itself, ensuring every station has a self-referential distance. The function 
        fetches distances from a DataFrame and augments it with a near-zero self-distance before 
        returning the sorted list of distances as a numpy array.

        :param station_id: Identifier for the station from which distances are to be retrieved
        :type station_id: int

        :returns: An array of distances sorted by station ID, including a minimal self-distance.
        :rtype: numpy.ndarray

        The method first filters a DataFrame for distances where the station is the origin, then appends 
        a minimal self-distance, and finally sorts these distances by destination station ID for uniformity. 
        This approach ensures that all distance data relevant to a particular station is consistent and 
        easily accessible.
        """
        distances_df = self.distances_df[self.distances_df['station_from'] == station_id]
        distances_df = pd.concat([distances_df, pd.DataFrame({'station_to': [station_id], 'distance': [1e-3]})], ignore_index=True)
        distances_arr = np.array(distances_df.sort_values(by='station_to')['distance'].values)
        return distances_arr

    
    def move_bike_surplus(self, station_from_surplus, station_to_df):
        """
        Determines the number of surplus bikes that can be moved from one station to another, 
        based on the probability of the destination station running out of bikes, the number of 
        available bike stands, and the current bike surplus at the origin station. The function 
        iteratively moves bikes until either the destination's probability of running out is reduced 
        to a safe level, the destination station's bike stands are full, or there are no more surplus 
        bikes to move.

        :param station_from_surplus: The number of surplus bikes available at the source station
        :type station_from_surplus: int
        :param station_to_df: DataFrame containing details about the destination station such as ID, 
                            run out probability, available bike stands, and number of bikes
        :type station_to_df: pandas.DataFrame

        :returns: A tuple containing:
                - The number of bikes moved
                - The updated number of surplus bikes at the source station after moving the bikes
                - The updated run out probability at the destination station
        :rtype: tuple

        The function first checks if the destination station is already at a low risk of running out 
        or if it is full. If neither condition is met, it moves bikes one by one from the source 
        to the destination, recalculating the run out probability with each move, until conditions 
        are met or surplus bikes are exhausted.
        """
        bikes_to_move = 0
        station_to_id = station_to_df['id']
        station_to_prob = station_to_df['run_out_prob']
        station_to_stands = station_to_df['available_bike_stands']
        station_to_bikes = station_to_df['available_bikes']
        if station_to_prob < self._critical_probability or station_to_bikes >= station_to_stands:
            return 0, station_from_surplus, station_to_prob
        while station_to_prob > self._critical_probability and station_from_surplus > 0 and station_to_bikes < station_to_stands:
            bikes_to_move += 1
            station_from_surplus -= 1
            station_to_prob = self.calculate_run_out_probability(station_to_id, bikes_to_move)
        return bikes_to_move, station_from_surplus, station_to_prob


    # stations_df --> dataframe with columns id, available_bikes, availablke_bike_stands
    # distances_df --> dataframe with columns station_from, station_to, distance
    def generate_recommendations(self):
        """
        Generates a list of recommended bike movements across stations to optimize bike availability and prevent stations from running out of bikes. The function calculates the run out probabilities for each station, identifies surplus bikes, and then moves them to other stations based on a priority score calculated from run out probability and distance.

        This function performs several operations including:
        - Copying the station dataframe and initializing a recommended moves column.
        - Calculating run out probabilities for all stations.
        - Iteratively selecting stations with surplus bikes and identifying target stations based on a calculated priority score.
        - Moving bikes and updating the status (available bikes, recommended moves, run out probabilities) of both source and target stations.

        :returns: A list of dictionaries where each dictionary contains 'station_from_id', 'station_to_id', and 'bikes_to_move' indicating the movements between stations.
        :rtype: list of dict

            The method loops a predefined number of times (self._maximum_moves), each time:
        - Selecting a source station based on the lowest run out probability.
        - Calculating bike surplus at the source station.
        - Determining the destination stations based on a priority score (run out probability divided by distance).
        - Moving bikes to optimize the distribution across the network.
        Each move is recorded and the database is updated in each iteration to reflect the changes.
        """        
        # Add a column to the stations dataframe with the total recommnended moves
        stations_df = self.stations_df.copy()
        stations_df['recommended_moves'] = 0
        
        # Calculate run out probabilities for all stations
        run_out_prob = []
        for station_id in stations_df['id']:
            moved_bikes = stations_df[stations_df['id'] == station_id]['recommended_moves'].values[0]
            run_out_prob.append(self.calculate_run_out_probability(station_id, moved_bikes))
        stations_df['run_out_prob'] = run_out_prob
        
        recommended_moves = []
        for k in range(self._maximum_moves):
            
            # Start from the station with the lowest probability of running out of bikes
            station_from_id = stations_df.sort_values(by='run_out_prob').iloc[0]['id']

            # Calculate the suplus of bikes at the selected station
            curr_available_bikes = stations_df[stations_df['id'] == station_from_id]['available_bikes'].values[0]
            curr_prob = stations_df[stations_df['id'] == station_from_id]['run_out_prob'].values[0]
            bike_surplus = self.calculate_bike_surplus(station_from_id, curr_available_bikes, curr_prob)

            # Get the distances from the selected station to all other stations
            distances_arr = self.get_station_distances(station_from_id)

            # Create a priority score for bike stations which is the run out probability divided by the distance
            prob_arr = np.array(stations_df.sort_values(by='id')['run_out_prob'].values)
            priority_arr = prob_arr / distances_arr
            stations_df['priority'] = priority_arr

            # Sort the bike stations by priority and remove the selected station
            sorted_stations_df = stations_df.sort_values(by='priority', ascending=False)
            sorted_stations_df = sorted_stations_df[sorted_stations_df['id'] != station_from_id]

            # Move bikes from the selected station to the next station in the sorted list
            i = 0
            curr_surplus = bike_surplus
            while curr_surplus > 0 and i < len(sorted_stations_df):
                station_to_df = sorted_stations_df.iloc[i]
                bikes_to_move, curr_surplus, station_to_prob = self.move_bike_surplus(curr_surplus, station_to_df)
                recommended_moves.append({
                    'station_from_id': station_from_id,
                    'station_to_id': station_to_df['id'],
                    'bikes_to_move': bikes_to_move
                })
                # Update the available bikes and run out probabilities in destination station
                station_to_id = station_to_df['id']
                stations_df.loc[stations_df['id'] == station_to_id, 'available_bikes'] += bikes_to_move
                stations_df.loc[stations_df['id'] == station_to_id, 'recommended_moves'] += bikes_to_move
                stations_df.loc[stations_df['id'] == station_to_id, 'run_out_prob'] = station_to_prob
                i += 1

            # Update the available bikes and run out probabilities in source station
            total_bikes_moved = bike_surplus - curr_surplus
            stations_df.loc[stations_df['id'] == station_from_id, 'available_bikes'] -= total_bikes_moved
            stations_df.loc[stations_df['id'] == station_from_id, 'recommended_moves'] -= total_bikes_moved
            stations_df.loc[stations_df['id'] == station_from_id, 'run_out_prob'] = self.calculate_run_out_probability(station_from_id, -total_bikes_moved)

        # Create a dataframe to remove the moves with 0 bikes and aggregate moves with same source and destination
        moves_df = pd.DataFrame(recommended_moves, columns=['station_from_id', 'station_to_id', 'bikes_to_move'])
        moves_df = moves_df[moves_df['bikes_to_move'] > 0]
        moves_df = moves_df.groupby(['station_from_id', 'station_to_id']).sum().reset_index()
        recommended_moves = moves_df.to_dict(orient='records') # List of dictionaries without the index

        return recommended_moves