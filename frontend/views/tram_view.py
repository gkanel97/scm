
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import json
import folium
import requests
from .views_Inerface import ViewInterface
import matplotlib.pyplot as plt
from utils.user_auth import UserAuthenticator


class TramView(ViewInterface):
    def __init__(self):
        super().__init__('Dublin Tram Stops Map')

    def fetch_data(self):
        cookie_manager = UserAuthenticator.get_manager("tram_fetch")
        headers = UserAuthenticator.prepare_api_headers(cookie_manager) 
        base_url = 'http://127.0.0.1:8000'
        url = f"{base_url}/api/tram/display"
        try:
            response = requests.post(url,headers=headers)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching data: {e}")
            return None

    def count_trams_on_line(self, df, line):
        #only get the rows where the line is the same as the input line
        df = df[df['line'].str.lower() == line.lower()]
        #apply the calculations to quantify the amount of trams on the line:
        total_trams = 0
        cutoff_index = []
        station_names = []
        for i in range(df.shape[0]-1):
            #previous
            p = df.iloc[i]['arrivals'][0]['arrival_time']
            #current
            c = df.iloc[i+1]['arrivals'][0]['arrival_time']
            #if previous or current are none, skip
            if (p == None) or (c == None):
                continue
            elif (p < c) or (p == c):
                continue
            elif p > c:
                #add the tram to the counter
                total_trams+=1
                #add the index to the cutoff index
                cutoff_index.append(i)
                #add the names of the station
                station_names.append(df.iloc[i]['stop_name'])
        return total_trams, cutoff_index, station_names

    def display_data(self, data):
        tram_stop_info = pd.DataFrame(data)

        station_coords = {}
        for _, row in tram_stop_info.iterrows():
            station_coords[row['stop_name']] = [row['latitude'], row['longitude']]

        m = folium.Map(location=[53.349805, -6.260310], zoom_start=12)
        for _, row in tram_stop_info.iterrows():
            color = 'green' if row['line'].lower() == 'green' else 'red'
            tooltip_content = f"Stop ID: {row['stop_id']}<br>" \
                              f"Stop Name: {row['stop_name']}<br>" \
                              f"Arrival Time: {row['arrivals'][0]['arrival_time']}<br>" \
                              f"Direction: {row['arrivals'][0]['direction']}<br>" \
                              f"Destination: {row['arrivals'][0]['destination']}<br>" \
                              f"Status: {row['arrivals'][0]['status']}"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                tooltip=folium.Tooltip(tooltip_content, style="font-family: Arial; color: black;")
            ).add_to(m)

        #Get the station names for red and green lines
        totalred, cutred, statred = self.count_trams_on_line(tram_stop_info, 'red')
        totalgreen, cutgreen, statgreen = self.count_trams_on_line(tram_stop_info, 'green')

        # Add tram markers between stations for red line
        for station in statred:
            if station in station_coords:
                station_index = tram_stop_info[tram_stop_info['stop_name'] == station].index[0]
                if station_index > 0:
                    prev_station = tram_stop_info.iloc[station_index - 1]['stop_name']
                    if prev_station in station_coords:
                        start_coords = station_coords[prev_station]
                        end_coords = station_coords[station]
                        midpoint_coords = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
                        folium.Marker(location=midpoint_coords, icon=folium.Icon(color='red', icon='train-tram', prefix='fa')).add_to(m)

        # Add tram markers between stations for green line
        for station in statgreen:
            if station in station_coords:
                station_index = tram_stop_info[tram_stop_info['stop_name'] == station].index[0]
                if station_index > 0:
                    prev_station = tram_stop_info.iloc[station_index - 1]['stop_name']
                    if prev_station in station_coords:
                        start_coords = station_coords[prev_station]
                        end_coords = station_coords[station]
                        midpoint_coords = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
                        folium.Marker(location=midpoint_coords, icon=folium.Icon(color='green', icon='train-tram', prefix='fa')).add_to(m)

        folium_static(m)

        selected_date = st.date_input("Select a date for passenger predictions:", min_value=pd.Timestamp('2024-01-01'), max_value=pd.Timestamp('2025-12-31'))
        line_option = st.selectbox('Select a tram line:', ['All Line', 'Red Line', 'Green Line'])

        if st.button('Show Passenger Predictions'):
            predictions = self.fetch_passenger_predictions(selected_date, line_option)
            if not predictions.empty:
                plt.figure(figsize=(10, 6))
                plt.plot(predictions['Hour'], predictions['Passengers'], marker='o')
                plt.title(f'Passenger Predictions for {selected_date.strftime("%Y-%m-%d")}')
                plt.xlabel('Hour of the Day')
                plt.ylabel('Number of Passengers')
                plt.xticks(range(5, 24), rotation=45)
                plt.grid(True)
                st.pyplot(plt)
            else:
                st.error("No passenger predictions available for the selected date.")

        # Testing code, returns the text in the console for now!
        print(f"Red trams cutoff stations: {statred}")
        print(f"Green trams cutoff stations: {statgreen}")
        print(f"Total red trams: {totalred}")
        print(f"Total green trams: {totalgreen}")
        print(cutred)
        print(cutgreen)

    def fetch_passenger_predictions(self, selected_date, selected_line):
        base_url = 'http://127.0.0.1:8000'
        url = f"{base_url}/api/tram/predictions"
        json_data = {
            "date": selected_date.strftime('%Y-%m-%d'),
            "line": selected_line
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=json_data, headers=headers)
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching passenger predictions: {e}")
            return pd.DataFrame({'Hour': [], 'Passengers': []})
