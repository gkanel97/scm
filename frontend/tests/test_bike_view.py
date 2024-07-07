import unittest
from unittest.mock import patch, Mock
from pandas import DataFrame
from views.bike_view import BikeView

class TestBikeView(unittest.TestCase):
    def setUp(self):
        self.bike_view = BikeView()

    @patch('views.bike_view.requests.get')
    def test_fetch_bike_data(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(return_value={'bike_station_data': []})
        mock_get.return_value = mock_resp

        result = self.bike_view.fetch_bike_data()
        self.assertIsInstance(result, DataFrame)

    @patch('views.bike_view.requests.post')
    def test_fetch_bike_predictions(self, mock_post):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(return_value={'bike_predictions': []})
        mock_post.return_value = mock_resp

        result = self.bike_view.fetch_bike_predictions("1")
        self.assertIsInstance(result, DataFrame)

    @patch('views.bike_view.requests.get')
    def test_fetch_recommendations(self, mock_get):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock()
        mock_resp.json = Mock(return_value={'bike_recommendations': []})
        mock_get.return_value = mock_resp

        result = self.bike_view.fetch_recommendations()
        self.assertIsInstance(result, dict)

if __name__ == '__main__':
    unittest.main()