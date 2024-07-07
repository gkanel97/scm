import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import requests
from .views_Inerface import ViewInterface
from utils.user_auth import UserAuthenticator
import json
from folium.plugins import MarkerCluster
class BikeView(ViewInterface):
    def __init__(self):
        super().__init__("Bike Station Information")


    def fetch_data(self):
        selection = st.selectbox("Choose Timestamp:", ["Real-time", "Next 1 hour", "Next 10 hours", "Next 24 hours"])
        if selection == "Real-time":
            real_time = True
            data = self.fetch_bike_data()
        else:
            real_time = False
            prediction_timedelta = selection.split(" ")[1]
            data = self.fetch_bike_predictions(prediction_timedelta)
        return data, real_time

    def display_data(self, data, realtime=True):
        if not data.empty:
            map = self.display_bikes_on_map(data, realtime)
            folium_static(map)
            if  st.button("Generate placement recommendations"):
                self.display_recommendations()
        else:
            st.error("No real-time data available at the moment. Please try again later.")


    @staticmethod
    def fetch_bike_data():
        url = 'http://127.0.0.1:8000/api/bikes/display'
        cookie_manager = UserAuthenticator.get_manager("bike")
        headers = UserAuthenticator.prepare_api_headers(cookie_manager)
        try:
            response = requests.get(url,headers=headers)
            response.raise_for_status()  # This will raise an exception for HTTP error responses
            data = response.json()
            bike_station_data = data['bike_station_data']
            return pd.DataFrame(bike_station_data)
        except requests.exceptions.RequestException as e:
            st.error(f"Error while fetching data: {e}")
            return pd.DataFrame()

    @staticmethod
    def fetch_bike_predictions(prediction_timedelta):
         with st.spinner("Generating predictions..."):
            try:
                url = 'http://127.0.0.1:8000/api/bikes/predictions'
                cookie_manager = UserAuthenticator.get_manager("bike")
                headers = UserAuthenticator.prepare_api_headers(cookie_manager)
                payload = {'forecast_timedelta': prediction_timedelta}
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()  # This will raise an exception for HTTP error responses
                data = response.json()
                bike_predictions = data['bike_predictions']
                return pd.DataFrame(bike_predictions)
            except requests.exceptions.RequestException as e:
                    st.error(f"Failed to fetch predictions from the backend: {e}")
                    return pd.DataFrame()

    @staticmethod
    def display_bikes_on_map(bike_data, real_time=True):
        m = folium.Map(location=[53.349805, -6.26031], zoom_start=13)
        for index, station in bike_data.iterrows():
            if pd.isnull(station['latitude']) or pd.isnull(station['longitude']):
                continue

            if real_time:
                bike_count = station['available_bikes']
                tooltip_msg = f"Available Bikes: {bike_count}"
            else:
                bike_count = station['prediction']
                tooltip_msg = f"Predicted Available Bikes: {bike_count}"

            color = 'green' if bike_count >= 5 else 'red'
            folium.Marker(
                location=[station['longitude'], station['latitude']],
                popup=f"{station['name']} - {tooltip_msg}",
                icon=folium.Icon(color=color),
                tooltip=tooltip_msg
            ).add_to(m)
        return m


    def display_recommendations(self):
        url = 'http://127.0.0.1:8000/api/bikes/recommendations/'   
        with st.spinner("Generating recommendations..."):
            try:
                # Fetch bike recommendations
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                bike_recommendations = data['bike_recommendations']
                bike_station_names = data['bike_stations']

                # Prepare data for visualization
                visualisation_data = []
                for recommendation in bike_recommendations:
                    from_id = str(recommendation['station_from_id'])
                    to_id = str(recommendation['station_to_id'])
                    visualisation_data.append([
                        bike_station_names[from_id],
                        bike_station_names[to_id],
                        recommendation['bikes_to_move']
                    ])

                # Create a DataFrame with human-readable column names
                recommend_df = pd.DataFrame(
                    visualisation_data,
                    columns=['From station', 'To station', 'Bikes to move']
                )

                # Display the recommendations
                st.write(recommend_df)

            except requests.exceptions.RequestException as e:
                st.error(f"Error while fetching data: {e}")