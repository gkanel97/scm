import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from views.bus_view import BusView

class TestBusView(unittest.TestCase):
    def setUp(self):
        self.bus_view = BusView()

    @patch('views.bus_view.st.multiselect')
    @patch('views.bus_view.st.checkbox')
    @patch('views.bus_view.st.plotly_chart')
    @patch('views.bus_view.requests.post')
    def test_fetch_and_display_data(self, mock_post, mock_plotly_chart, mock_checkbox, mock_multiselect):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{'route_short_name': '1', 'Early': 10, 'On time': 20, 'Short delay': 30, 'Medium delay': 40, 'Long delay': 50}]
        mock_post.return_value = mock_resp
        mock_multiselect.return_value = ['Route 1']
        mock_checkbox.return_value = True

        result = self.bus_view.fetch_data()
        self.assertIsInstance(result, list)

        self.bus_view.display_data(result)

        mock_plotly_chart.assert_called()

if __name__ == '__main__':
    unittest.main()