import unittest
from unittest.mock import patch, Mock
from datetime import datetime
from views.pedestrian_view import PedestrianView
import pandas as pd
import folium

class TestPedestrianView(unittest.TestCase):
    def setUp(self):
        self.pedestrian_view = PedestrianView()

    @patch('views.pedestrian_view.st.date_input')
    @patch('views.pedestrian_view.st.selectbox')
    @patch('views.pedestrian_view.requests.post')
    def test_fetch_data(self, mock_post, mock_selectbox, mock_date_input):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json = Mock(return_value={'pedestrian_predictions': []})
        mock_post.return_value = mock_resp
        mock_date_input.return_value = datetime.now()
        mock_selectbox.return_value = "12:00"

        result = self.pedestrian_view.fetch_data()
        self.assertIsInstance(result, list)

    @patch('views.pedestrian_view.pd.read_csv')
    @patch('views.pedestrian_view.folium.Map')
    @patch('views.pedestrian_view.folium_static')
    def test_display_data(self, mock_folium_static, mock_map, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame({'Street': ['street1'], 'Latitude': [53.349805], 'Longitude': [-6.260310]})
        mock_map.return_value = folium.Map(location=[53.349805, -6.260310], zoom_start=13)
        mock_folium_static.return_value = None

        self.pedestrian_view.display_data({'street1': 10})

if __name__ == '__main__':
    unittest.main()