import requests
import jwt
import time
import json
from http import HTTPStatus
import os
import streamlit as st
import extra_streamlit_components as stx
import time as t
#constants
AUTH_EP = 'http://127.0.0.1:8000/api/auth/login_user'
REF_EP = 'http://127.0.0.1:8000/api/auth/refresh_token'


@st.cache_resource(experimental_allow_widgets=True)
# def get_cookie_manager():
#     return stx.CookieManager()

class UserAuthenticator():


    # def __init__(self):
    #     # self.cookies = get_cookie_manager()
        

    def authenticate(self, username, password):
        '''
        ### User authentication
        1. params :  username and password
        2. returns:  tokens.
        Description : The function accepts username and password and makes an api call to authentication,
                      and checks. 

        '''
        user_data = {"username": username, "password":password}
        auth_response = requests.post(AUTH_EP, json = user_data)
        if auth_response.status_code == HTTPStatus.OK:
            tokens = auth_response.json()
            return {'status': 'success', 'access_token': tokens['access_token'], 'refresh_token': tokens['refresh_token']}
        elif auth_response.status_code == HTTPStatus.UNAUTHORIZED:
            return {'status': 'unauthorized'}
        else:
            return {'status': 'error'}
        

    @st.cache_resource
    def get_refresh_token(_self):
        return st.session_state.access_token, st.session_state.refresh_token

    def check_if_tokens_expired(self, token):
        '''
        ### Member function.

        This function is used to check the expiery of access tokens and return Ture if expired else False.
        '''

        try:
            payload = jwt.decode(token, options={"verify_signature": False})

            current_time = time.time()

            return current_time > payload['exp']
        
        except(jwt.ExpiredSignatureError, jwt.DecodeError):

            return True

    def get_new_access_token(self, ref_token):

        '''
        ### Get new access token - member function

        This function will request backend api for new access token if refresh token is still valid
        else will return null object.
        '''

        is_ref_tkn_valid = self.check_if_tokens_expired(ref_token)

        if not is_ref_tkn_valid:
            return None
        else:
            data = {'refresh': ref_token}
            new_access_token = requests.post(REF_EP, json=data)
            if new_access_token.status_code == HTTPStatus.OK:
                return new_access_token
        return None
    
    def register(self, username, password, role):

        data = {"username": username, "password": password, "group": role }

        api_response = requests.post(url='http://127.0.0.1:8000/api/auth/create_user', json=data)

        if api_response.status_code == HTTPStatus.CREATED:
            return {'status': 'created'}
        elif api_response.status_code == HTTPStatus.BAD_REQUEST:
            return {'status': 'taken-username'}
        else:
            return {'status': 'error'}
    @staticmethod
    def prepare_api_headers(cookie_manager):
            """
            Prepares and returns the headers needed for making authenticated API calls,
            specifically the Authorization header with a bearer token. Uses the provided
            UserAuthenticator and cookie_manager to retrieve the necessary tokens.

            Parameters:
            - user_authenticator: An instance of UserAuthenticator used to manage user authentication.
            - cookie_manager: An instance of a cookie manager obtained from the UserAuthenticator,
            used to retrieve authentication tokens.

            Returns:
            - headers (dict): A dictionary of headers with the Authorization included.
            """
            t.sleep(0.1)
            # Retrieve the access token using the provided cookie_manager
            access_token = cookie_manager.get("access_token")
            t.sleep(0.1)

            # Construct the Authorization header
            if(access_token == None):
                return {}
            headers = {"Authorization": "Bearer " + access_token}
            
            return headers
    
    @staticmethod
    # @st.cache_resource
    def get_manager(unique_key):
        manager_key = f"cookie_manager_{unique_key}"
        return stx.CookieManager(key=manager_key)



            
