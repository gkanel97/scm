import streamlit as st
from utils import user_auth
import time
import extra_streamlit_components as stx

class Widgets:
    '''
    ### Widgets

    This class contains all the widgets for end-user interaction
    '''
    @staticmethod
    # @st.cache_resource
    def get_manager(unique_key):
        manager_key = f"cookie_manager_{unique_key}"
        return stx.CookieManager(key=manager_key)


    TOKENS = None
    def __init__(self):
        self.auth = user_auth.UserAuthenticator()

    def login(self):
        '''
        ### Login widget
        This widget is used to accept user name and passwrod from end user.
        '''

        col1, col2 , col3 = st.columns([1, 2, 1])
        cookie_manager = Widgets.get_manager("login")

        with col2:  

            st.title("Login/Signup")
            
            login_form = st.form(key='login')
            username = login_form.text_input("Username")
            password = login_form.text_input("Password",type='password')
            
            col_1, col_2 = login_form.columns(2)
            
            with col_1: 
                login_button = login_form.form_submit_button("Login")
                
            with col_2:
                signup_button = login_form.form_submit_button("Sign Up") 
                
            if login_button:
                #login logic
                resp = self.auth.authenticate(username=username, password=password)
                if resp['status'] == 'unauthorized':
                    st.error("Invalid username or password")
                    return
                elif resp['status'] == 'error':
                    st.error("An error occured. Please try again later.")
                    return
                else:
                    access_token = resp.get('access_token', None)
                    refresh_token = resp.get('refresh_token', None)
                    
                    if access_token is None or refresh_token is None:
                        st.error("An error occured. Please try again later.")
                        return
                    
                    cookie_manager.set("access_token",access_token,key="set_access_token",path='/')
                    cookie_manager.set("refresh_token",refresh_token,key="set_refresh_token", path="/")
                    time.sleep(0.04)
                    # cookie_manager.update()
                    st.success("Logged In")
                    st.session_state.is_logged_in = True
                    st.rerun()
            
            if signup_button:
                #signup logic   
                resp = self.auth.register(username=username, password=password, role='cm')

                if resp['status'] == 'success':
                    st.success("User created")
                    st.rerun()
                elif resp['status'] == 'taken-username':
                    st.error("User already exists")
                else:
                    st.error("An error occured. Please try again later.")          
