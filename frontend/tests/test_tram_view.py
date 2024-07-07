import unittest
from unittest.mock import patch, MagicMock
from pandas.testing import assert_frame_equal
import pandas as pd
from views.tram_view import TramView
from streamlit_folium import st_folium
import folium

class TestTramView(unittest.TestCase):
    @patch('requests.post')
    def test_fetch_data(self, mock_post):
        # Mock the response from requests.post
        mock_post.return_value.json.return_value = {'key': 'value'}
        mock_post.return_value.raise_for_status.return_value = None

        tram_view = TramView()
        data = tram_view.fetch_data()

        # Check if the returned data is a dictionary
        self.assertIsInstance(data, dict)

    def test_count_trams_on_line(self):
        tram_view = TramView()
        df = pd.DataFrame({
            'line': ['red', 'green', 'red', 'green'],
            'arrivals': [[{'arrival_time': '10:00'}], [{'arrival_time': '11:00'}], [{'arrival_time': '12:00'}], [{'arrival_time': '13:00'}]]
        })

        total_trams, cutoff_index, station_names = tram_view.count_trams_on_line(df, 'red')


        # Check if the returned values are as expected
        self.assertEqual(total_trams, 0)
        self.assertEqual(cutoff_index, [])
        self.assertEqual(station_names, [])


    @patch('requests.post')
    def test_fetch_passenger_predictions(self, mock_post):
        # Mock the response from requests.post
        mock_post.return_value.json.return_value = [{'Hour': 1, 'Passengers': 10}]
        mock_post.return_value.raise_for_status.return_value = None

        tram_view = TramView()
        predictions = tram_view.fetch_passenger_predictions(pd.Timestamp('2024-01-01'), 'All Line')

        # Check if the returned data is a DataFrame and has the expected content
        assert_frame_equal(predictions, pd.DataFrame([{'Hour': 1, 'Passengers': 10}]))

if __name__ == '__main__':
    unittest.main()