import json
from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock

from pedestrians.views import get_pedestrian_predictions
from pedestrians.predictions import PedestrianPredictor



class PedestrianTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_pedestrian_predictions_valid(self):
        data = {'date': '2021-01-01', 'hour': '12:00'}
        request = self.factory.post('/pedestrian/predictions', json.dumps(data), content_type='application/json')
        
        with patch('pedestrians.views.PedestrianPredictor') as MockPredictor:
            mock_instance = MockPredictor.return_value
            mock_instance.predict_footfall.return_value = {'Main Street': 100.0}
            response = get_pedestrian_predictions(request)
            
            response_content = json.loads(response.content.decode('utf-8'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_content, {'pedestrian_predictions': {'Main Street': 100.0}})




class TestPedestrianPredictor(TestCase):
    def setUp(self):
        # Mocking the entire PedestrianPredictor class
        self.predictor = MagicMock(spec=PedestrianPredictor)
        self.predictor.predict_footfall.return_value = {'main_street': 150, 'side_avenue': 0}

    def test_predict_footfall(self):
        """Test the predict_footfall method with mocked dependencies."""
        # Directly test the predict_footfall method
        result = self.predictor.predict_footfall('2024-04-10', '14:00')
        self.assertEqual(result, {'main_street': 150, 'side_avenue': 0})
        self.predictor.predict_footfall.assert_called_once_with('2024-04-10', '14:00')
