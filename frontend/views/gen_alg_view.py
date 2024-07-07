import requests
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, time
from utils.user_auth import UserAuthenticator
from views.views_Inerface import ViewInterface

class GeneticAlgorithmView(ViewInterface):
    def __init__(self):
        super().__init__("Timetable Optimisation")

    def fetch_data(self):
        cookie_manager = UserAuthenticator.get_manager("bus_timetable")
        headers = UserAuthenticator.prepare_api_headers(cookie_manager) 
        url = 'http://127.0.0.1:8000/api/bus/timetable'

        with st.form(key='route_optimisation_form'):
            first_route_date = st.date_input("First Route Date", datetime.now())
            first_route_time = st.time_input("First Route Time", time())
            last_route_date = st.date_input("Last Route Date", datetime.now())
            last_route_time = st.time_input("Last Route Time", time())
            target_services = st.number_input("Target Number of Services", min_value=1, value=1, step=1)

            submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            first_route_datetime = datetime.combine(first_route_date, first_route_time)
            last_route_datetime = datetime.combine(last_route_date, last_route_time)

            if first_route_datetime > last_route_datetime:
                st.error("First route time cannot be after the last route time")
                return None
            if (last_route_datetime - first_route_datetime).total_seconds() > 3600 * 24:
                st.error("The route time range cannot be more than 1 day")
                return None
            if (last_route_datetime - first_route_datetime).total_seconds() < 3600:
                st.error("The route time range cannot be less than 1 hour")
                return None
            if target_services <20:
                st.error("The target number of services should be greater than 20")
                return None

            
            request_body = {
                'first_bus': first_route_datetime.strftime('%Y-%m-%d %H:%M'),
                'last_bus': last_route_datetime.strftime('%Y-%m-%d %H:%M'),
                'target_services': target_services
            }
            try:
                response = requests.post(url, json=request_body, headers=headers)
                if response.status_code != 200:
                    st.error(f"Failed to fetch predictions: {response.text}")
                    return None
                timetable_list = response.json()['optimal_timetables']
                return timetable_list
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch predictions: {e}")
                return None

    def display_data(self, data):
        if data is not None:
            timetable_arr = []
            tab_list = []
            for i, timetable in enumerate(data):
                departure_dict = {}
                for departure in timetable['timetable']:
                    departure_time = datetime.strptime(departure, '%Y-%m-%dT%H:%M:%S')
                    hour = departure_time.hour
                    minute = departure_time.minute
                    if hour not in departure_dict:
                        departure_dict[hour] = set([minute])
                    else:
                        departure_dict[hour].add(minute)

                # Convert the sets to strings
                for key in departure_dict:
                    departure_dict[key] = ['  '.join([str(x) for x in sorted(departure_dict[key])])]

                timetable_df = pd.DataFrame.from_dict(departure_dict, orient='index')
                timetable_df.columns = ['Departure Minutes']
                timetable_df.index.name = 'Hour'

                num_services = timetable['num_services']
                waiting_time = timetable['waiting_time']

                timetable_arr.append((num_services, waiting_time, timetable_df))
                tab_list.append(f'Timetable {i+1}')

            st.write('#### Optimal Timetables')

            op = st.tabs(tab_list)
            for i in range(len(tab_list)):
                with op[i]:
                    num_services, waiting_time, timetable_df = timetable_arr[i]
                    st.write(f'Number of services = {num_services} | Average waiting time = {int(np.ceil(waiting_time))} minutes')
                    st.dataframe(timetable_df)
        else:
            st.write("No data available to display.")

