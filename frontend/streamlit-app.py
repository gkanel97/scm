import time
import streamlit as st
import extra_streamlit_components as stx

from widgets import login, dashboard
from utils.user_auth import UserAuthenticator

wid = login.Widgets()
db = dashboard.Dashboard()

userauth = UserAuthenticator()
cookie_manager = userauth.get_manager("main")
access_token = cookie_manager.get("access_token")
refresh_token = cookie_manager.get("refresh_token")
time.sleep(0.04)

if access_token != "" and (not userauth.check_if_tokens_expired(access_token)):
    db.display_dashboard()
elif refresh_token != "" and (not userauth.check_if_tokens_expired(refresh_token)):
    nat = userauth.get_new_access_token(refresh_token)
    cookie_manager.set("access_token" , nat, key="access_token")
    db.display_dashboard()
else:
    wid.login()