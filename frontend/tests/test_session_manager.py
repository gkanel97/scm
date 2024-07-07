import unittest
from unittest.mock import patch, MagicMock
from authenticator.session_manager import SessionMgr
import os

# Mock environment variable for REF_TKN_EP
os.environ['REF_TKN_EP'] = 'https://example.com/refresh'

class TestSessionMgr(unittest.TestCase):


    @patch('authenticator.session_manager.requests.post')
    @patch('authenticator.session_manager.time.time')
    @patch('authenticator.session_manager.CookieManager')
    def test_refresh_access_token(self, mock_cookie_manager, mock_time, mock_post):
        # Mock time to control the expiry calculation
        mock_time.return_value = 1000  # Simulating a specific point in time

        # Mock the response from requests.post to simulate API call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'new_access_token'}
        mock_post.return_value = mock_response

        # Mock CookieManager methods
        mock_cookie_manager_instance = mock_cookie_manager.return_value
        mock_cookie_manager_instance.get.side_effect = lambda key: 'existing_token' if key in ['refresh_token', 'access_token'] else None

        session_mgr = SessionMgr()

        # Ensure refresh_token is set for testing
        session_mgr.refresh_token = 'existing_refresh_token'

        # Call refresh_access_token and verify behavior
        result = session_mgr.refresh_access_token()
        self.assertTrue(result)
        self.assertEqual(session_mgr.access_token, 'new_access_token')
        # Considering mock time set to 1000, expiry should be set correctly
        expected_expiry = 1000 + (15 * 60)  # Adding 15 minutes to the mock time
        self.assertEqual(session_mgr.access_token_expiry, expected_expiry)

        # Verify CookieManager set was called correctly
        mock_cookie_manager_instance.set.assert_called_with('access_token', 'new_access_token')

    # Additional tests to cover _get_refresh_token_cookie, _get_access_token_cookie, and get_new_access_token methods
    # Ensure to mock CookieManager.get method in each to return appropriate values
    # and mock time.time() as needed to simulate time for token expiry checks


    @patch('authenticator.session_manager.CookieManager')
    def test_get_refresh_token_cookie(self, mock_cookie_manager):
        mock_cookie_manager.return_value.get.return_value = 'mock_refresh_token'
        
        session_mgr = SessionMgr()

        refresh_token = session_mgr._get_refresh_token_cookie()

        self.assertEqual(refresh_token, 'mock_refresh_token')

    @patch('authenticator.session_manager.CookieManager')
    def test_get_access_token_cookie(self, mock_cookie_manager):
        mock_cookie_manager.return_value.get.return_value = 'mock_access_token'
        
        session_mgr = SessionMgr()

        access_token = session_mgr._get_access_token_cookie()

        self.assertEqual(access_token, 'mock_access_token')

    @patch('authenticator.session_manager.st.error')
    @patch('authenticator.session_manager.SessionMgr.refresh_access_token')
    @patch('authenticator.session_manager.time.time')
    @patch('authenticator.session_manager.CookieManager')
    def test_get_new_access_token_no_refresh_needed(self, mock_cookie_manager, mock_time, mock_refresh_access_token, mock_st_error):
        mock_time.return_value = 1000  # Current time for the context of this test
        mock_cookie_manager_instance = mock_cookie_manager.return_value
        mock_cookie_manager_instance.get.return_value = 'valid_access_token'  # Mocked return value for the cookie

        session_mgr = SessionMgr()
        session_mgr.access_token_expiry = 1100  # Set expiry time to the future

        access_token = session_mgr.get_new_access_token()

        self.assertEqual(access_token, 'valid_access_token')
        mock_refresh_access_token.assert_not_called()
    
    @patch('authenticator.session_manager.st.error')
    @patch('authenticator.session_manager.SessionMgr.refresh_access_token', return_value=False)
    @patch('authenticator.session_manager.time.time', return_value=1000)
    @patch('authenticator.session_manager.CookieManager')
    def test_get_new_access_token_refresh_failed(self, mock_cookie_manager_instance, mock_time, mock_refresh_access_token, mock_st_error):
        # Configure the mock for CookieManager instance methods
        mock_cookie_manager_instance.get.side_effect = lambda x: None  # Simulate no access token available

        session_mgr = SessionMgr()

        # Force the access token to be considered expired to trigger a refresh
        session_mgr.access_token_expiry = 900  # Past time, indicating expired token
        
        # Attempt to get a new access token, expecting the refresh to fail
        session_mgr.get_new_access_token()

        # Verify that the refresh access token method was called
        mock_refresh_access_token.assert_called_once()


if __name__ == '__main__':
    unittest.main()
