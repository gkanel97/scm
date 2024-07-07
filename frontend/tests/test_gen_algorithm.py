import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, time
from views.gen_alg_view import GeneticAlgorithmView

class TestGeneticAlgorithmView(unittest.TestCase):
    def setUp(self):
        self.gen_alg_view = GeneticAlgorithmView()

    @patch('views.gen_alg_view.st.form')
    @patch('views.gen_alg_view.st.date_input')
    @patch('views.gen_alg_view.st.time_input')
    @patch('views.gen_alg_view.st.number_input')
    @patch('views.gen_alg_view.st.form_submit_button')
    @patch('views.gen_alg_view.requests.post')
    def test_fetch_data(self, mock_post, mock_form_submit_button, mock_number_input, mock_time_input, mock_date_input, mock_form):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'optimal_timetables': []}
        mock_post.return_value = mock_resp
        mock_form_submit_button.return_value = True
        mock_date_input.return_value = datetime.now().date()
        mock_time_input.side_effect = [time(hour=12), time(hour=13)]
        mock_number_input.return_value = 30

        result = self.gen_alg_view.fetch_data()
        self.assertIsInstance(result, list)

    @patch('views.gen_alg_view.st.tabs')
    @patch('views.gen_alg_view.st.dataframe')
    @patch('views.gen_alg_view.st.write')
    def test_display_data(self, mock_write, mock_dataframe, mock_tabs):
        mock_tabs.return_value = [MagicMock()]
        mock_dataframe.return_value = None
        mock_write.return_value = None

        self.gen_alg_view.display_data([{'timetable': ['2022-01-01T12:00:00'], 'num_services': 30, 'waiting_time': 60}])

if __name__ == '__main__':
    unittest.main()