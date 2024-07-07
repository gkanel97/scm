import time
import streamlit as st
import extra_streamlit_components as stx
from widgets.homepage import SustainableCityDashboard
from views.pedestrian_view import PedestrianView
from views.gen_alg_view import GeneticAlgorithmView
from views.bus_view import BusView
from views.bike_view import BikeView
from views.tram_view import TramView
import time


class Dashboard:
    count=0
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def get_manager(unique_key):
        manager_key = f"cookie_manager_{unique_key}"
        return stx.CookieManager(key=manager_key)
    
    def logout(self):
        st.title("Logout Page")
        st.success("Logout successful!")
        cookie_manager = Dashboard.get_manager("logout")
        
        cookie_manager.set("access_token","",key="access_token_logout")
        cookie_manager.set("refresh_token","",key="refresh_token_logout")
        time.sleep(0.04)        
        st.rerun()

    def display_dashboard(self):
        st.sidebar.image("widgets/sustainableCitydashboard.png", use_column_width=True)
        st.sidebar.write("### Navigation")
        # Custom CSS to embed in the web page to style the container of the radio buttons
        radio_button_container_styles = """
        <style>
            div.row-widget.stRadio > div {
                border: 2px solid white;
                border-radius: 4px;
            }
        </style>
        """

        # Inject custom styles into the web page.
        st.markdown(radio_button_container_styles, unsafe_allow_html=True)

        with st.sidebar:
            tabs = ["Homepage", "Bike Data", "Tram Data", "Bus Data", "Pedestrian Data", "Timetable Optimisation"]
            radio_container = st.container()
            with radio_container:
                current_tab = st.radio("", tabs, index=0)
        if current_tab == "Homepage":
            dashboard = SustainableCityDashboard()
            dashboard.run()
        elif current_tab == "Bike Data":
            st.title("Bike Dashboard")
            bike_view = BikeView()
            data , realtime=bike_view.fetch_data()
            bike_view.display_data(data,realtime)
        elif current_tab == "Tram Data":
            st.title("Tram Dashboard")
            tram_view = TramView()
            tram_view.display_data(tram_view.fetch_data())
        elif current_tab == "Bus Data":
            st.title("Bus Dashboard")
            bus_view_instance = BusView()
            bus_view_instance.display_data(bus_view_instance.fetch_data())
        elif current_tab == "Pedestrian Data":
            st.title("Pedestrian Dashboard")
            pedestrian_view = PedestrianView()
            pedestrian_view.display_data(pedestrian_view.fetch_data())
        elif current_tab == "Timetable Optimisation":
            st.title("Timetable Optimisation for Bus Dashboard")
            gen_alg_view =GeneticAlgorithmView()
            gen_alg_view.display_data(gen_alg_view.fetch_data())
        if st.sidebar.button("Logout"):
            self.logout()

