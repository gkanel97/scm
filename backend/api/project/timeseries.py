import numpy as np
from sklearn.linear_model import LinearRegression

class TimeSeriesModel:
    def __init__(self, previous_days_to_consider=2):
        """
        Initializes the time series model with the specified number of previous days to consider.

        :param previous_days_to_consider: The number of previous days to consider for prediction.
        :type previous_days_to_consider: int
        """
        self.previous_days_to_consider = previous_days_to_consider
        self.model = LinearRegression()

    def predict_bikes_usage(self, arrayOfUsagePerDay):
        """
        Predicts bike usage for the next day based on the usage data of previous days.

        :param arrayOfUsagePerDay: Array containing bike usage data for each day.
        :type arrayOfUsagePerDay: list of int
        :return: Predicted bike usage for the next day.
        :rtype: int
        """
        X, y = [], []

        for i in range(len(arrayOfUsagePerDay) - self.previous_days_to_consider):
            train_part = arrayOfUsagePerDay[i:i + self.previous_days_to_consider]
            test_part = arrayOfUsagePerDay[i + self.previous_days_to_consider]
            X.append(train_part)
            y.append(test_part)

        X, y = np.array(X), np.array(y)
        X = X.reshape(-1, self.previous_days_to_consider)

        self.model.fit(X, y)

        to_predict = np.array(arrayOfUsagePerDay[-self.previous_days_to_consider:]).reshape(1, -1)
        y_pred = self.model.predict(to_predict)

        return int(np.ceil(y_pred[0]))
