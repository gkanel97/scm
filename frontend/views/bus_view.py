import json
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from .views_Inerface import ViewInterface
from utils.user_auth import UserAuthenticator

class BusView(ViewInterface):
    def __init__(self):
        super().__init__("Bus Delay Visualization")

    def fetch_data(self):
        # Fetch bus delay data
        cookie_manager = UserAuthenticator.get_manager("bus")
        headers = UserAuthenticator.prepare_api_headers(cookie_manager)
        url = 'http://127.0.0.1:8000/api/bus/display'
        now = datetime(2024, 3, 21, 21, 0, 0)
        data = {
            'start_time': now.strftime('%Y-%m-%d') + ' 04:00', # Start at 4am
            'end_time': now.strftime('%Y-%m-%d %H:%M') # End at the current time
        }
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        return resp.json()

    def display_data(self, data):
        delay_df = pd.DataFrame(data)

        if delay_df.empty:
            st.write('No data available')
            return

        # Make sure route numbers are treated as strings
        delay_df['route_short_name'] = 'Route ' + delay_df['route_short_name'].astype(str)
        route_names = delay_df['route_short_name'].unique()

        route_selection = st.multiselect('Select Route Numbers', route_names)
        normalize_view = st.checkbox('Show Normalized Data')
        if route_selection:

            # Keep only the selected routes
            filtered_delay_df = delay_df[delay_df['route_short_name'].isin(route_selection)]

            # Normalize the data if the checkbox is checked
            if normalize_view:
                total_counts = filtered_delay_df[['Early', 'On time', 'Short delay', 'Medium delay', 'Long delay']].sum(axis=1)
                for column in ['Early', 'On time', 'Short delay', 'Medium delay', 'Long delay']:
                    filtered_delay_df[column] = (filtered_delay_df[column] / total_counts) * 100

            # Create a stacked bar chart
            fig = px.bar(
                filtered_delay_df,
                x='route_short_name',
                y=['Early', 'On time', 'Short delay', 'Medium delay', 'Long delay'],
                barmode='stack',
                labels={'value': 'Count', 'variable': 'Delay Type'},
                title='Bus Delays by Route'
            )
            fig.update_layout(
                title='Bus Delays by Route' if not normalize_view else 'Normalized Bus Delays by Route',
                xaxis_title='Route Number',
                yaxis_title='Proportion of Delays (%)' if normalize_view else 'Number of Delays'
            )
            st.plotly_chart(fig)