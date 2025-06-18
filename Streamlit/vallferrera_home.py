import streamlit as st
import pandas as pd
import os
from functions import *

# Define the data path and the zone
processing_data_path = '../../Data/Processing-Data'
zone = 'vallferrera'

# Output data path
df_path = os.path.join(processing_data_path, zone, 'Output-Data', 'Data-Frames', 'tracks_info.csv')
df = pd.read_csv(df_path)

def app():
    st.title("La Vall Ferrera")

    # Sidebar page selector
    page = st.sidebar.radio("Navigate", ("Home", "Questions and Answers", "Individual Tracks"))

    # Routing logic
    if page == "Home":
        zone_home_page(zone, df)
    elif page == "Questions and Answers":
        zone_questions_and_answers(zone, df)
    elif page == "Individual Tracks":
        zone_individual_tracks(zone, df)