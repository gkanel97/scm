from django.test import TestCase, RequestFactory
from .views import get_tram_display_data, get_tram_recommendations
import pandas as pd 

class TramTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_tram_data(self):
        request = self.factory.get('/api/tram/display')
        response = get_tram_display_data(request)
        self.assertEqual(response.status_code, 200)
        tram_data = response.json()
        df = pd.DataFrame(tram_data)
        
        #to check whether the length of both are equal
        self.assertEqual(len(df), len(df.drop_duplicates()))

        #to check whether there are missing values
        self.assertFalse(df.isnull().values.any())