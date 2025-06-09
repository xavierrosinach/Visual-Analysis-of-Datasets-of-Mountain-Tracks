import streamlit as st
import pandas as pd
import sys
import os

# Get the path of the visualizatoins directory to obtain the functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Visualizations')))

# Import the visualizations library
from non_spatial import *

# Define the data path and the zone
data_path = '../../Data'
zone = 'canigo'

# Output data path
df_path = os.path.join(data_path, zone, 'Output-Data', 'Data-Frames', 'tracks_info.csv')
df = pd.read_csv(df_path)

# Function to obtain the values to highlight
def obtain_values_highlight(zone):

    # Obtain the dataframe path and read it
    df_path = f'../../Data/{zone}/Output-Data/Data-Frames/tracks_info.csv'
    df = pd.read_csv(df_path)

    # Obtain the different metrics
    total_tracks = f"{len(df)} tracks"      # Total tracks as the lenght of the dataframe
    mean_dist = f"{round(df['total_distance'].mean(), 2)} km"      # Mean of the distance in km
    mean_time = df['total_time'].mean()     # Mean time in minutes, later we will transform it in hh:mm
    mean_pace = df['average_pace'].mean()       # Mean average pace in minutes, later we will transform it in mm:ss
    mean_elevation_gain = f"{round(df['elevation_gain'].mean())} m"   # Mean elevation gain in meters

    # Change the variable mean_time with the desired format
    hours = int(mean_time // 60)
    minutes = int(mean_time % 60)
    
    # Depend if the hours are greater or not of 0
    if hours > 0:
        form_time = f"{hours}h {minutes}min"
    else:
        form_time = f"{minutes}min"

    # Change the variable mean_pace with the desired format
    total_seconds = int(round(mean_pace * 60))      # Obtain the total seconds
    minutes = total_seconds // 60       # Extract minutes
    seconds = total_seconds % 60        # Extract seconds
    form_pace = f"{minutes}:{seconds:02d} min/km"       # Obtain the formatted pace

    # Obtain a time range as this example "from October 2012 to January 2025"
    df['date'] = pd.to_datetime(df['date'])     # Dataframe column in datetime

    # Obtain the minimum and maximum date string
    min_str = df['date'].min().strftime('%B %Y')
    max_str = df['date'].max().strftime('%B %Y')

    # Create the time range string
    time_range = f"from {min_str} to {max_str}"

    return total_tracks, mean_dist, form_time, form_pace, mean_elevation_gain, time_range

def home_page(tracks_str, dist_str, time_str, pace_str, elev_str, time_range_str):
    st.subheader("Home Page")
    st.image("Images/canigo_home.jpg")
    st.write("Escriure aquí informació rellevant sobre el Canigó. Afegir una imatge, també.")

    # First metrics row
    col1, col2 = st.columns(2)
    col1.metric(label="Total tracks", value=tracks_str)
    col2.metric(label="Time range", value=time_range_str)

    # Second metrics row
    col3, col4 = st.columns(2)
    col3.metric(label="Average activity distance", value=dist_str)
    col4.metric(label="Average activity time", value=time_str)

    # Third metrics row
    col5, col6 = st.columns(2)
    col5.metric(label="Average activity pace", value=pace_str)
    col6.metric(label="Average activity elevation gain", value=elev_str)

def non_spatial_vis():
    st.subheader("Non-Spatial Visualizations")

    st.write("Explicació")

    # Expander for the time distribution
    with st.expander("Time distribution"):
        st.altair_chart(time_distribution(df))
        st.info("Explicació Chart", icon=":material/info:")

    # Expander for the two years comparison - start with the last and the previous year
    with st.expander("Two years comparison"):
        # En aquest cas s'ha de crear un botó per a poder anar movent els anys
        months_comparison, weekdays_comparison = two_years_comparisons(df, 2023, 2024)
        st.altair_chart(months_comparison)
        st.info("Explicació Chart", icon=":material/info:")
        st.altair_chart(weekdays_comparison)
        st.info("Explicació Chart", icon=":material/info:")

    # Expander for the monthly weather conditions
    with st.expander("Monthly weather conditions"):

        # Crear dos botons per anar passant
        st.altair_chart(calendar_weather(df, 2024, 'Jan'))
        st.info("Explicació Chart", icon=":material/info:")

    # Expander for the difficulty distribution
    with st.expander("Difficulty distribution"):

        # Crear botons per seleccionar els dos eixos
        st.altair_chart(difficulty_scatter(df, 'total_distance', 'elevation_gain'))
        st.info("Explicació Chart", icon=":material/info:")

    # Expander for the tracks distribution
    with st.expander("Quantitative variables trends"):
        st.altair_chart(all_quantitative_histograms(df))
        st.info("Explicació Chart", icon=":material/info:")

def spatial_vis():
    st.subheader("Spatial Visualizations")

def individual_tracks():
    st.subheader("Individual Tracks")

def app():
    st.title("El Canigó")

    # Apply the function obtain_values_highlight to avoid the execution each time we go to the Home page
    tracks, dist, time, pace, elev, time_ran = obtain_values_highlight('canigo')

    # Sidebar page selector
    page = st.sidebar.radio("Navigate", ("Home", "Non-Spatial Visualizations", "Spatial Visualizations", "Individual Tracks"))

    # Routing logic
    if page == "Home":
        home_page(tracks, dist, time, pace, elev, time_ran)
    elif page == "Non-Spatial Visualizations":
        non_spatial_vis()
    elif page == "Spatial Visualizations":
        spatial_vis()
    elif page == "Individual Tracks":
        individual_tracks()
    