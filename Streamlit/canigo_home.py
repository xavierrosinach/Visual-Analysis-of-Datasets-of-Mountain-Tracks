import streamlit as st
import pandas as pd
import os
from functions import *

# Define the data path and the zone
processing_data_path = '../../Data/Processing-Data'
zone = 'canigo'

# Output data path
df_path = os.path.join(processing_data_path, zone, 'Output-Data', 'Data-Frames', 'tracks_info.csv')
df = pd.read_csv(df_path)

def app():
    st.title("El Canigó")

    # Obtain all the visualizations
    time_dist_vis, month_comp_vis, weekday_comp_vis, diff_info_vis, weather_vis, all_edges_map, diff_edges_maps, weather_edges_maps, years_edges_maps = create_visualizations(zone)

    # Sidebar page selector
    page = st.sidebar.radio("Navigate", ("Home", "Questions and Answers", "Individual Tracks"))

    # Routing logic
    if page == "Home":
        zone_home_page(zone, df)
    elif page == "Questions and Answers":
        zone_questions_and_answers(zone, time_dist_vis, month_comp_vis, weekday_comp_vis, diff_info_vis, weather_vis, all_edges_map, diff_edges_maps, weather_edges_maps, years_edges_maps)
    elif page == "Individual Tracks":
        zone_individual_tracks(zone, df)
    