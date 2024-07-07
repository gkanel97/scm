from .views_Inerface import ViewInterface
import folium
import requests
import pandas as pd
import streamlit as st
from http import HTTPStatus
from datetime import datetime
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

class PedestrianView(ViewInterface):
    def __init__(self):
        super().__init__("Pedestrian Footfall Prediction")

    def fetch_data(self):
        start_date = st.date_input("Select date for prediction:", datetime.now())
        hour = st.selectbox("Select hour for prediction:", [f"{h}:00" for h in range(24)])
        
        url = 'http://127.0.0.1:8000/api/pedestrian/predictions'
        request_body = {
            'date': start_date.strftime('%Y-%m-%d'),
            'hour': hour
        }
        response = requests.post(url, json=request_body)
        if response.status_code != HTTPStatus.OK:
            st.error(f"Failed to fetch predictions: {response.text}")
            return None
        return response.json()['pedestrian_predictions']

    def display_data(self, predictions):
        if predictions:
            street_locations = pd.read_csv('views/data/streets.csv')
            street_map = folium.Map(location=[53.349805, -6.260310], zoom_start=13)
            marker_cluster = MarkerCluster().add_to(street_map)
            
            for _, location in street_locations.iterrows():
                street_name = location['Street']
                lat, lon = location['Latitude'], location['Longitude']
                predicted_footfall = predictions.get(street_name)

                predicted_footfall_str = f"{predicted_footfall}" if predicted_footfall is not None else "No data"

                popup_content = f"{street_name}: Predicted Footfall: {predicted_footfall_str}"
                popup = folium.Popup(popup_content, max_width=300)
                tooltip_text = f"{street_name}: Predicted Footfall: {predicted_footfall_str}"

                folium.Marker(
                    [lat, lon],
                    popup=popup,
                    tooltip=tooltip_text
                ).add_to(marker_cluster)

            folium_static(street_map)
        else:
            st.error("No data available for the selected date and hour.")

   
