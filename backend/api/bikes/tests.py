import json
import pandas as pd
from datetime import datetime, timezone

from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.urls import reverse

from unittest.mock import patch, MagicMock, mock_open

from .models import BikeStation, BikeAvailability
from .views import *
import unittest
import numpy as np


class BikeDisplayDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.station_1 = BikeStation.objects.create(
            id=1, 
            name='Station 1', 
            latitude=40.7128,
            longitude=-74.0060,
            capacity=10
        )
        cls.station_2 = BikeStation.objects.create(
            id=2,
            name='Station 2',
            latitude=40.7338,
            longitude=-73.9910,
            capacity=15
        )
        BikeAvailability.objects.create(
            station=cls.station_1,
            harvest_time='2024-03-12T12:00:00Z',
            last_update_time='2024-03-12T12:00:00Z',
            available_bike_stands=5,
            available_bikes=5,
            status='Open'
        )
        BikeAvailability.objects.create(
            station=cls.station_2,
            harvest_time='2024-03-12T12:00:00Z',
            last_update_time='2024-03-12T12:00:00Z',
            available_bike_stands=10,
            available_bikes=5,
            status='Open'
        )

    def test_get_latest_bike_availability(self):
        from bikes.views import get_latest_bike_availability

        latest_data = get_latest_bike_availability()
        self.assertEqual(len(latest_data), 2) 

        # Test station 1
        station_1_data = next((data for data in latest_data if data['id'] == 1), None)
        self.assertIsNotNone(station_1_data)
        self.assertEqual(station_1_data['name'], 'Station 1')
        self.assertEqual(station_1_data['latitude'], 40.7128)
        self.assertEqual(station_1_data['longitude'], -74.0060)
        self.assertEqual(station_1_data['capacity'], 10)
        self.assertEqual(station_1_data['available_bikes'], 5)
        self.assertEqual(station_1_data['available_bike_stands'], 5)
        self.assertEqual(station_1_data['last_update_time'], datetime(2024, 3, 12, 12, 0, tzinfo=timezone.utc))

        # Test station 2 (with null values)
        station_2_data = next((data for data in latest_data if data['id'] == 2), None)
        self.assertIsNotNone(station_2_data)
        self.assertEqual(station_2_data['name'], 'Station 2')
        self.assertEqual(station_2_data['latitude'], 40.7338)
        self.assertEqual(station_2_data['longitude'], -73.9910)
        self.assertEqual(station_2_data['capacity'], 15)
        self.assertEqual(station_2_data['available_bikes'], 5)
        self.assertEqual(station_2_data['available_bike_stands'], 10)
        self.assertEqual(station_2_data['last_update_time'], datetime(2024, 3, 12, 12, 0, tzinfo=timezone.utc))

    def test_get_bike_display_data(self):
        factory = RequestFactory()
        request = factory.get(reverse('get_bike_display_data'))

        response = get_bike_display_data(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = json.loads(response.content)
        self.assertIn('bike_station_data', response_data)
        bike_station_data = response_data['bike_station_data']
        self.assertEqual(len(bike_station_data), 2)

        # Test station 1
        station_1_data = next((data for data in bike_station_data if data['id'] == 1), None)
        self.assertIsNotNone(station_1_data)
        self.assertEqual(station_1_data['name'], 'Station 1')
        self.assertEqual(station_1_data['latitude'], 40.7128)
        self.assertEqual(station_1_data['longitude'], -74.0060)
        self.assertEqual(station_1_data['capacity'], 10)
        self.assertEqual(station_1_data['available_bikes'], 5)
        self.assertEqual(station_1_data['available_bike_stands'], 5)
        self.assertEqual(station_1_data['last_update_time'], '2024-03-12T12:00:00Z')

        # Test station 2
        station_2_data = next((data for data in bike_station_data if data['id'] == 2), None)
        self.assertIsNotNone(station_2_data)
        self.assertEqual(station_2_data['name'], 'Station 2')
        self.assertEqual(station_2_data['latitude'], 40.7338)
        self.assertEqual(station_2_data['longitude'], -73.9910)
        self.assertEqual(station_2_data['capacity'], 15)
        self.assertEqual(station_2_data['available_bikes'], 5)
        self.assertEqual(station_2_data['available_bike_stands'], 10)
        self.assertEqual(station_2_data['last_update_time'], '2024-03-12T12:00:00Z')


class GetBikeRecommendationsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.bike_stations_data = [
            {'id': 1, 'name': 'Central Station', 'latitude': 40.7128, 'longitude': -74.0060, 'capacity': 20},
            {'id': 2, 'name': 'North Station', 'latitude': 40.7338, 'longitude': -73.9910, 'capacity': 15}
        ]

    @patch('bikes.views.get_latest_bike_availability')
    @patch('bikes.views.load_prophet_models')
    @patch('bikes.models.BikeDistance.objects.all')
    def test_get_bike_recommendations(self, mock_distances, mock_load_models, mock_latest_avail):
        mock_latest_avail.return_value = [
            {'id': 1, 'name': 'Station 1', 'latitude': 40.0, 'longitude': -75.0, 'capacity': 15, 'available_bikes': 5, 'available_bike_stands': 10},
            {'id': 2, 'name': 'Station 2', 'latitude': 41.0, 'longitude': -74.0, 'capacity': 10, 'available_bikes': 8, 'available_bike_stands': 2}
        ]
        mock_distances.return_value.values.return_value = [
            {'station_from': 1, 'station_to': 2, 'distance': 1000},
            {'station_from': 2, 'station_to': 1, 'distance': 1000}
        ]
        mock_load_models.return_value = {1: MockModel(), 2: MockModel()}

        request = self.factory.get('/')
        response = get_bike_recommendations(request)
        response_data = json.loads(response.content.decode())

        self.assertEqual(response.status_code, 200)
        self.assertIn('bike_recommendations', response_data)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='binary data here')
    @patch('pickle.load')
    def test_load_prophet_models(self, mock_pickle_load, mock_open, mock_exists):
        mock_exists.return_value = True
        mock_pickle_load.return_value = {'model_id': 'model_data'}
        models = load_prophet_models('fake_path/prophet_model.pkl')
        mock_exists.assert_called_once_with('fake_path/prophet_model.pkl')
        mock_open.assert_called_once_with('fake_path/prophet_model.pkl', 'rb')
        self.assertEqual(models, {'model_id': 'model_data'})

    @patch('bikes.views.load_prophet_models')
    @patch('bikes.models.BikeStation.objects.values')
    def test_get_bike_predictions(self, mock_values, mock_load_models):
        request_data = {'forecast_timedelta': 5}
        request = self.factory.post('/', json.dumps(request_data), content_type='application/json')

        mock_model_1 = MagicMock()
        mock_model_2 = MagicMock()
        mock_model_1.predict.return_value = pd.DataFrame({'yhat': [10.5]})
        mock_model_2.predict.return_value = pd.DataFrame({'yhat': [7.8]})
        mock_load_models.return_value = {1: mock_model_1, 2: mock_model_2}
        mock_values.return_value = self.bike_stations_data

        response = get_bike_predictions(request)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(len(response_data['bike_predictions']), 2)
        self.assertIn('prediction', response_data['bike_predictions'][0])
        self.assertEqual(response_data['bike_predictions'][0]['prediction'], 10)
        self.assertEqual(response_data['bike_predictions'][1]['prediction'], 8)  


class MockModel:
    def predict(self, df):
        return pd.DataFrame({
            'ds': df['ds'],
            'yhat': [10 for _ in df['ds']],
            'yhat_lower': [8 for _ in df['ds']],
            'yhat_upper': [12 for _ in df['ds']]
        })


class TestBikeRecommender(unittest.TestCase):
    def setUp(self):
        self.stations_df = pd.DataFrame({
            'id': [1, 2, 3],
            'available_bikes': [15, 5, 20],
            'available_bike_stands': [10, 20, 15]
        })

        self.distances_df = pd.DataFrame({
            'station_from': [1, 1, 2, 2, 3, 3],
            'station_to': [2, 3, 1, 3, 1, 2],
            'distance': [1000, 1500, 1000, 500, 1500, 500]
        })

        self.forecast_model = MagicMock()
        self.timestamps_to_predict = pd.date_range("2024-01-01", periods=3, freq='H')

        self.recommender = BikeRecommender(
            stations_df=self.stations_df,
            distances_df=self.distances_df,
            forecast_model=self.forecast_model,
            timestamps_to_predict=self.timestamps_to_predict
        )
        self.recommender._critical_threshold = 5
        self.recommender._surplus_probability = 0.35
        self.recommender._maximum_moves = 3


    def test_calculate_run_out_probability_no_bikes(self):
        station_id = 2
        bike_moves = -1 
        run_out_prob = self.recommender.calculate_run_out_probability(station_id, bike_moves)

        self.assertEqual(run_out_prob, 1.0, "Run-out probability should be 1.0 when there are no available bikes.")


    def test_calculate_bike_surplus(self):
        surplus = self.recommender.calculate_bike_surplus(1, 20, 0.1)
        self.assertTrue(0 < surplus < 15)

    def test_get_station_distances(self):
        test_cases = [
            (1, np.array([1e-3, 1000, 1500])),
            (2, np.array([1e-3, 500, 1000]))
        ]
        for station_id, expected_distances in test_cases:
            actual_distances = self.recommender.get_station_distances(station_id)
            
            expected_distances.sort()
            actual_distances.sort()
            
            np.testing.assert_array_almost_equal(actual_distances, expected_distances, decimal=4,
                                                err_msg=f"Distances do not match expected values for station {station_id}")
            

    def test_generate_recommendations(self):
        self.recommender.calculate_run_out_probability = MagicMock(return_value=0.1)
        self.recommender.calculate_bike_surplus = MagicMock(return_value=5)
        self.recommender.get_station_distances = MagicMock(return_value=np.array([0.001, 500, 1000]))
        



