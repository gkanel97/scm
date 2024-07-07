import pickle
import numpy as np
import pandas as pd
from datetime import datetime

_PREDICTIVE_MODEL_PATH = 'pedestrians/analytics/pedestrian_model.pkl'

class PedestrianPredictor():

    def __init__(self):
        """
        Initializes the instance by loading predictive models from a binary file.
        The models are stored in a predefined file path (`_PREDICTIVE_MODEL_PATH`), which is a class attribute.
        These models are deserialized using pickle and stored in the instance variable `self.models` for later use.

        :param self: Reference to the current instance of the class.
        :type self: instance
        """
        with open(_PREDICTIVE_MODEL_PATH, 'rb') as file:
            self.models = pickle.load(file)
        
    def predict_footfall(self, date, hour):
        """
        Predicts pedestrian footfall for each street using preloaded models. This method processes each model corresponding to different streets,
        constructs a future date-time scenario, and then applies the model to predict footfall for that scenario.

        :param self: Reference to the current instance of the class.
        :type self: instance
        :param date: The date for which footfall prediction is required, in 'YYYY-MM-DD' format.
        :type date: str
        :param hour: The hour for which footfall prediction is required, specified in 'HH:MM' format.
        :type hour: str

        :returns: A dictionary with street names as keys and predicted footfall values as values. Ensures all footfall values are non-negative.
        :rtype: dict
        """
        predictions = {}
        for street_name in self.models.keys():

            # Remove the suffix '_model' and replace underscores with spaces to match the 'Street' names
            formatted_street_name = street_name.replace("_model", "").replace(" ", '_').replace('/','_')
            
            # Constructing a DataFrame with the expected format
            date_time_str = f"{date} {hour}"
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
            future = pd.DataFrame({'ds': [date_time_obj]})
            
            # Use the model to make predictions
            forecast = self.models[street_name].predict(future)
            predicted_footfall = forecast['yhat'].iloc[0]

            # Make sure that the predictions are always positive
            predictions[formatted_street_name] = np.maximum(predicted_footfall, 0) 

        return predictions