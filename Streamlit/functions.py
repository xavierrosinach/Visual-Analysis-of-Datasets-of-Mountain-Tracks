import pandas as pd
import streamlit as st
import altair as alt
import sys
import os
from PIL import Image
from streamlit.components.v1 import html

# Define the data path
streamlit_data_path = '../../Data/Streamlit-Data'
processing_data_path = '../../Data/Processing-Data'

# Go to the 'Visualizations' folder to obtain the functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Visualizations')))

# Import the functions
from non_spatial import *
from spatial import *

# Given the zone, creates all the visualizations
def create_visualizations(zone):

    # Obtain the dataframes
    tracks_info = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Data-Frames', 'tracks_info.csv'))
    weather_df = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Data-Frames', 'weather.csv'))

    # Time distribution vis
    year_bar_chart, month_bar_chart, all_dates_line = time_distribution(tracks_info)    # Generate the visualizations
    year_bar_chart = year_bar_chart.properties(width=400, height=200, title='Registered Tracks per Year')                   # Sizes and titles
    month_bar_chart = month_bar_chart.properties(width=400, height=200, title='Registered Tracks per Month')
    all_dates_line = all_dates_line.properties(width=900, height=200, title='Evolution of Registered Tracks Through the Years')
    time_dist_vis = alt.vconcat(alt.hconcat(year_bar_chart, month_bar_chart), all_dates_line).resolve_scale(x='shared').configure_view(strokeOpacity=0)

    # Two years comparisons
    month_comp_vis = two_years_month_comparison(tracks_info)
    weekday_comp_vis = two_years_weekday_comparison(tracks_info)

    # Difficulty information
    difficulty_bars, min_max_lines, scatter_grid = difficulty_info(tracks_info)
    difficulty_bars = difficulty_bars.properties(width=300, height=300, title='Total registered tracks per difficulty')
    diff_info_vis = alt.hconcat(alt.vconcat(difficulty_bars, min_max_lines), scatter_grid).resolve_scale(x='shared').configure_view(strokeOpacity=0)

    # Weather information - read HTML as does not work well
    weather_vis_path = os.path.join(streamlit_data_path, 'Visualizations', zone, 'Non-Spatial-Visualizations', 'weather_calendar.html')
    with open(weather_vis_path, "r", encoding="utf-8") as f:
        weather_vis = f.read()

    # Full map visualization - in HTML
    full_map_path = os.path.join(streamlit_data_path, 'Visualizations', zone, 'Edges-Maps-Visualizations', 'all_edges_map.html')
    with open(full_map_path, "r", encoding="utf-8") as f:
        all_edges_map = f.read()
    
    # All difficulties
    difficulties = ['easy', 'moderate', 'difficult', 'very_difficult']
    diff_edges_maps = []
    for diff in difficulties:
        map_path = os.path.join(streamlit_data_path, 'Visualizations', zone, 'Edges-Maps-Visualizations', f'{diff}_edges.html')
        with open(map_path, "r", encoding="utf-8") as f:
            map = f.read()
            diff_edges_maps.append(map)

    # All weather conditions
    weather_cond = ['clear','cloudy','drizzle','rain','snow']
    weather_edges_maps = []
    for weath in weather_cond:
        map_path = os.path.join(streamlit_data_path, 'Visualizations', zone, 'Edges-Maps-Visualizations', f'{weath}_edges.html')
        with open(map_path, "r", encoding="utf-8") as f:
            map = f.read()
            weather_edges_maps.append(map)

    # All years
    years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    years_edges_maps = []
    for year in years:
        map_path = os.path.join(streamlit_data_path, 'Visualizations', zone, 'Edges-Maps-Visualizations', f'{year}_edges.html')
        if os.path.exists(map_path):
            with open(map_path, "r", encoding="utf-8") as f:
                map = f.read()
                years_edges_maps.append(map)
        else:
            years_edges_maps.append(None)

    # Return all the data
    return time_dist_vis, month_comp_vis, weekday_comp_vis, diff_info_vis, weather_vis, all_edges_map, diff_edges_maps, weather_edges_maps, years_edges_maps

# Function to obtain the values to highlight
def obtain_values_highlight(df):

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

# Function to create the home page for the zone
def zone_home_page(zone, df):

    st.subheader("Home Page")
    st.markdown('---')

    # Read the txt file to write the info
    with open(f'{streamlit_data_path}/Text/{zone}/intro.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)

    st.markdown('---')

    st.subheader('Data of the Zone')

    # Apply the function obtain_values_highlight to avoid the execution each time we go to the Home page
    tracks_str, dist_str, time_str, pace_str, elev_str, time_range_str = obtain_values_highlight(df)

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

    st.markdown('---')

    st.subheader('Images of the Zone')

    # Path with the images
    path_images = os.path.join(streamlit_data_path, 'Images', zone)

    # Filter valid extensions
    valid_exts = ('.png', '.jpg', '.jpeg')
    image_files = [f for f in os.listdir(path_images) if f.lower().endswith(valid_exts)]
    image_files.sort()

    # Create a grid 5x2 to show the images
    cols = st.columns(2)  # 2 columns
    for i in range(5):
        for j in range(2):
            idx = i * 2 + j
            image_path = os.path.join(path_images, image_files[idx])
            image = Image.open(image_path)
            with cols[j]:
                st.image(image, use_column_width=True)

    st.markdown('---')

# Question 1 function
def question_1(zone, all_edges_map):

    # Header
    st.header('Full Network of Paths Map')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q1.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    st.markdown('---')

    # Show the path
    html(all_edges_map, height=800, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q1.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 2 function
def question_2(zone, diff_edges_maps):
    
    # Header
    st.header('Network of Paths Maps depending on the Difficulty')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q2.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    
    st.markdown('---')

    # First row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Easy")
        html(diff_edges_maps[0], height=400, scrolling=False)

    with col2:
        st.markdown("#### Moderate")
        html(diff_edges_maps[1], height=400, scrolling=False)

    # Second row
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Difficult")
        html(diff_edges_maps[2], height=400, scrolling=False)

    with col4:
        st.markdown("#### Very difficult")
        html(diff_edges_maps[3], height=400, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q2.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 3 function
def question_3(zone, years_edges_maps):
    
    # Header
    st.header('Network of Paths Maps depending on the Year')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q3.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    st.markdown('---')

    if zone != 'matagalls':

        # Plot using rows
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2012")
            html(years_edges_maps[0], height=400, scrolling=False)
        with col2:
            st.markdown("#### 2013")
            html(years_edges_maps[1], height=400, scrolling=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2014")
            html(years_edges_maps[2], height=400, scrolling=False)
        with col2:
            st.markdown("#### 2015")
            html(years_edges_maps[3], height=400, scrolling=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2016")
            html(years_edges_maps[4], height=400, scrolling=False)
        with col2:
            st.markdown("#### 2017")
            html(years_edges_maps[5], height=400, scrolling=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2018")
            html(years_edges_maps[6], height=400, scrolling=False)
        with col2:
            st.markdown("#### 2019")
            html(years_edges_maps[7], height=400, scrolling=False)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2020")
            html(years_edges_maps[8], height=400, scrolling=False)
        with col2:
            st.markdown("#### 2021")
            html(years_edges_maps[9], height=400, scrolling=False)

    # Row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 2022")
        html(years_edges_maps[10], height=400, scrolling=False)
    with col2:
        st.markdown("#### 2023")
        html(years_edges_maps[11], height=400, scrolling=False)

    # Row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 2024")
        html(years_edges_maps[12], height=400, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q3.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')
    
# Question 4 function
def question_4(zone, weather_edges_maps):
    
    # Header
    st.header('Network of Paths Maps depending on the Weather Condition')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q4.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    
    st.markdown('---')

    # First row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Clear")
        html(weather_edges_maps[0], height=400, scrolling=False)
    with col2:
        st.markdown("#### Cloudy")
        html(weather_edges_maps[1], height=400, scrolling=False)

    # Second row
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Drizzle")
        html(weather_edges_maps[2], height=400, scrolling=False)
    with col4:
        st.markdown("#### Rain")
        html(weather_edges_maps[3], height=400, scrolling=False)

    # Third row
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### Snow")
        html(weather_edges_maps[4], height=400, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q4.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 5 function
def question_5(zone, diff_info_vis):
    
    # Header
    st.header('Difficulty Distribution and Correlation with Quantitative Variables')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q5.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    
    st.markdown('---')

    # Show the path
    st.altair_chart(diff_info_vis, use_container_width=True)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q5.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)
    
    st.markdown('---')

# Question 6.1 function
def question_6_1(zone, time_dist_vis):

    # Header
    st.header('Time distribution')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q6.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)

    st.markdown('---')

    # Header
    st.markdown('#### Distribution of the Registered Tracks through the Time')

    # Show the path
    st.altair_chart(time_dist_vis, use_container_width=True)

# Question 6.2 function
def question_6_2(zone, month_comp_vis):

    st.markdown('---')

    # Header
    st.markdown('#### Two Years Registered Tracks Comparison between Months')

    # Show the path
    st.altair_chart(month_comp_vis, use_container_width=True)

# Question 6.3 function
def question_6_3(zone, weekday_comp_vis):

    st.markdown('---')

    # Header
    st.markdown('#### Two Years Registered Tracks Comparison between Weekdays')

    # Show the path
    st.altair_chart(weekday_comp_vis, use_container_width=True)
    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q6.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 7 function
def question_7(zone, weather_vis):

    # Header
    st.header('Weather Conditions Distribution')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q7.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    st.markdown('---')

    # Show the path
    html(weather_vis, height=800, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q7.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

def zone_questions_and_answers(zone, time_dist_vis, month_comp_vis, weekday_comp_vis, diff_info_vis, weather_vis, all_edges_map, diff_edges_maps, weather_edges_maps, years_edges_maps):

    st.subheader("Questions and Answers")
    st.markdown('---')

    # Introduction
    with open(f'{streamlit_data_path}/Text/General/intro_questions.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)

    st.markdown('---')

    # Dictionary with questions and functions to execute
    questions = {
        "1. Which are the most commonly used start and end points in each area, and which route segments are the most frequented? Can we identify areas where people frequently stop?": lambda: question_1(zone, all_edges_map),
        "2. Are some sections avoided depending on difficulty?": lambda: question_2(zone, diff_edges_maps),
        "3. Does the usage of certain paths change over time?": lambda: question_3(zone, years_edges_maps),
        "4. Are some paths used depending on the weather conditions?": lambda: question_4(zone, weather_edges_maps),
        "5. Can we correlate the perceived difficulty with different quantitative variables? What is the distribution of these variables?": lambda: question_5(zone, diff_info_vis),
        "6. How has the number of recorded routes evolved throughout the year, and which periods show the highest activity?": lambda: (question_6_1(zone, time_dist_vis), question_6_2(zone, month_comp_vis), question_6_3(zone, weekday_comp_vis)),
        "7. What is the relationship between weather conditions and the number of recorded routes?": lambda: question_7(zone, weather_vis)}

    # Select box to select the question
    selected_question = st.selectbox("Select a question to explore", list(questions.keys()))

    st.markdown('---')

    # Mostrar respuesta al hacer clic
    with st.spinner("Loading answer..."):
        questions[selected_question]() 

# Returns the track ID visualizations
def track_visualizations(zone, df, track_id):

    # Obtain the single track map path and dataframes
    map_path = f'{streamlit_data_path}/Visualizations/{zone}/Single-Tracks-Visualizations/{track_id}_map.html'
    full_track_df = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Tracks-Output', 'All-Tracks', f'{track_id}.csv'))
    track_km_df = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Tracks-Output', 'Partial-Km', f'{track_id}.csv'))
    track_pace_df = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Tracks-Output', 'Partial-Pace', f'{track_id}.csv'))
    track_edges_df = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Tracks-Output', 'Partial-Edges', f'{track_id}.csv'))

    # General dataframes - all edges and waypoints
    all_edges_df = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Data-Frames', 'Edges-Dataframes', 'all_edges.csv'))
    waypoints_df = pd.read_csv(os.path.join(processing_data_path, zone, 'Output-Data', 'Data-Frames', 'waypoints.csv'))

    # Filter the dataframe to get only the track information
    track_info = df[df['track_id'] == track_id]

    # Check if exists
    if len(track_info) < 1:
        st.error(f'The track with ID {track_id} does not exist. Please enter a correct ID.')
        return

    with st.status(f'Generating visualizations for the track with ID {track_id}...', expanded=False):

        # Title and headers
        st.header(f'Single track visualizations and information of the track with ID {track_id}')
        st.subheader(f'{track_info['title'].iloc[0]}')
        st.markdown(f'[Link to Wikiloc]({track_info['url'].iloc[0]})')

        st.markdown("---")

        # Obtain the values to highlight
        tracks_str, dist_str, time_str, pace_str, elev_str, time_range_str = obtain_values_highlight(track_info)

        st.subheader('General Track Data')

        # Print the info: distance, time, pace, elevation, date, and URL
        # First metrics row
        col1, col2 = st.columns(2)
        col1.metric(label="Date", value=pd.to_datetime(track_info['date'].iloc[0]).strftime('%d %b %Y'))
        col2.metric(label="Distance", value=(track_info['difficulty'].iloc[0]))

        # Second metrics row
        col3, col4 = st.columns(2)
        col3.metric(label="Distance", value=dist_str)
        col4.metric(label="Time", value=time_str)

        # Third metrics row
        col5, col6 = st.columns(2)
        col5.metric(label="Average pace", value=pace_str)
        col6.metric(label="Elevation gain", value=elev_str)

        st.markdown("---")

        # Insert title
        st.subheader(f'Elevation Profile and Pace Bars for the Track {track_id}')

        # Obtain the visualization and show it
        elevation_vis = elevation_profile_and_pace_bars(full_track_df, track_km_df)
        st.altair_chart(elevation_vis, use_container_width=True)

        st.markdown("---")

        # Insert title
        st.subheader(f'Path of the Track {track_id}')

        # Write the introduction
        with open(f'{streamlit_data_path}/Text/General/intro_individual_vis2.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        st.markdown(content)

        # Create the map and show it
        track_map = create_track_map(track_id, df, all_edges_df, waypoints_df, full_track_df, track_km_df, track_pace_df, track_edges_df)
        map_html = track_map._repr_html_()      # Map to HTML
        html(map_html, height=800, scrolling=False)     # Show the map

        st.markdown('---')

# Function to create the individual tracks page for the zone
def zone_individual_tracks(zone, df):

    st.subheader("Individual Tracks")
    st.markdown('---')

    # Write introduction
    with open(f'{streamlit_data_path}/Text/General/intro_individual.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)

    # Select the columns to show
    df['track_id'] = df['track_id'].astype(str)
    showed_df = df[['track_id','title','date','difficulty','total_distance','total_time','average_pace','elevation_gain','url']]
    showed_df = showed_df.sort_values(by='date')

    # Show the datafame formatted
    st.dataframe(showed_df,  
                 hide_index=True,
                 column_config={'track_id':st.column_config.TextColumn('Track ID'),
                                'title':st.column_config.TextColumn('Title'),
                                'date':st.column_config.DateColumn('Date', format="DD MMM YYYY"),
                                'difficulty':st.column_config.TextColumn('Difficulty'),
                                'total_distance':st.column_config.NumberColumn('Distance', format="%.2f km"),
                                'total_time':st.column_config.NumberColumn('Time', format="%d min"),
                                'average_pace':st.column_config.NumberColumn('Average pace', format="%.2f min/km"),
                                'elevation_gain':st.column_config.NumberColumn('Elevation gain', format="%d m"),
                                'url': st.column_config.LinkColumn("URL")})

    st.markdown('---')

    # Text input
    track_id = st.text_input("Type a correct track ID to see the visualizations:")

    if track_id:
        track_visualizations(zone, df, track_id)
    
    st.markdown('---')

