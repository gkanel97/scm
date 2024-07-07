import streamlit as st

class SustainableCityDashboard:
    def __init__(self):
        self.title = "Sustainable City Management Dashboard"

    def display_header(self):
        st.markdown(f"<h1 style='text-align: center;'>{self.title}</h1>", unsafe_allow_html=True)
        st.subheader("Facilitating efficiency with data-driven insights.")

    def display_transportation_modes(self):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image("icons/bikes_icon.png", width=100)
        with col2:
            st.image("icons/buses_icon.png", width=100)
        with col3:
            st.image("icons/trams_icon.png", width=100)
        with col4:
            st.image("icons/pedestrians_icon.png", width=100)

    def display_description(self):
        st.markdown("""
        - **Bikes**: Utilise a predictive model to forecast the short term availability of bikes on specific stations. Generate recommendations that assist in dynamic bike redistribution.
        - **Buses**: Classify historical delays and display them on an interactive visualisation for every bus route.
        - **Trams**: Employ an optimisation algorithm to output a pareto-efficient timetable, with multiple options for the trnasport providers and city managers to select depending on their requirements.
        - **Pedestrians**: Use a time series predictive model to identify pedestrian footfall for specific areas at a specific time provided.
        """)

    def run(self):
        self.display_header()
        self.display_transportation_modes()
        self.display_description()

if __name__ == "__main__":
    dashboard = SustainableCityDashboard()
    dashboard.run()
