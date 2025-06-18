import pandas as pd
import streamlit as st
import altair as alt
from streamlit.components.v1 import html

# Define the data path
streamlit_data_path = '../../Data/Streamlit-Data'

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

    st.markdown('---')

# Question 1 function
def question_1(zone, df):

    # Header
    st.header('Full Network of Paths Map')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q1.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    st.markdown('---')

    # HTML path
    chart_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/all_edges_map.html'

    # Show the path
    with open(chart_path, "r", encoding="utf-8") as f:
        chart_html = f.read()
    html(chart_html, height=800, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q1.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 2 function
def question_2(zone, df):
    
    # Header
    st.header('Network of Paths Maps depending on the Difficulty')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q2.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    
    st.markdown('---')

    # Get all the paths
    easy_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/easy_edges.html'
    moderate_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/moderate_edges.html'
    difficult_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/difficult_edges.html'
    very_difficult_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/very_difficult_edges.html'

    # First row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Easy")
        with open(easy_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    with col2:
        st.markdown("#### Moderate")
        with open(moderate_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    # Second row
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Difficult")
        with open(difficult_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    with col4:
        st.markdown("#### Very difficult")
        with open(very_difficult_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q2.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 3 function
def question_3(zone, df):
    
    # Header
    st.header('Network of Paths Maps depending on the Year')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q3.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    st.markdown('---')

    if zone != 'matagalls':

        # Get all the years paths
        path_2012 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2012_edges.html'
        path_2013 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2013_edges.html'
        path_2014 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2014_edges.html'
        path_2015 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2015_edges.html'
        path_2016 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2016_edges.html'
        path_2017 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2017_edges.html'
        path_2018 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2018_edges.html'
        path_2019 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2019_edges.html'
        path_2020 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2020_edges.html'
        path_2021 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2021_edges.html'

        # Plot using rows
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2012")
            with open(path_2012, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        with col2:
            st.markdown("#### 2013")
            with open(path_2013, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2014")
            with open(path_2014, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        with col2:
            st.markdown("#### 2015")
            with open(path_2015, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2016")
            with open(path_2016, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        with col2:
            st.markdown("#### 2017")
            with open(path_2017, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2018")
            with open(path_2018, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        with col2:
            st.markdown("#### 2019")
            with open(path_2019, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 2020")
            with open(path_2020, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)
        with col2:
            st.markdown("#### 2021")
            with open(path_2021, "r", encoding="utf-8") as f:
                html(f.read(), height=400, scrolling=False)

    # Get the other years paths
    path_2022 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2022_edges.html'
    path_2023 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2023_edges.html'
    path_2024 = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/2024_edges.html'

    # Row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 2022")
        with open(path_2022, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    with col2:
        st.markdown("#### 2023")
        with open(path_2023, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    # Row
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### 2024")
        with open(path_2024, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q3.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')
    
# Question 4 function
def question_4(zone, df):
    
    # Header
    st.header('Network of Paths Maps depending on the Weather Condition')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q4.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    
    st.markdown('---')

    # Get all the paths
    clear_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/clear_edges.html'
    cloudy_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/cloudy_edges.html'
    drizzle_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/drizzle_edges.html'
    rain_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/rain_edges.html'
    snow_path = f'{streamlit_data_path}/Visualizations/{zone}/Edges-Maps-Visualizations/clear_edges.html'

    # First row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Clear")
        with open(clear_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    with col2:
        st.markdown("#### Cloudy")
        with open(cloudy_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    # Second row
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Drizzle")
        with open(drizzle_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    with col4:
        st.markdown("#### Rain")
        with open(rain_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    # Third row
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("#### Snow")
        with open(snow_path, "r", encoding="utf-8") as f:
            html(f.read(), height=400, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q4.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 5 function
def question_5(zone, df):
    
    # Header
    st.header('Difficulty Distribution and Correlation with Quantitative Variables')
    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q5.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)
    
    st.markdown('---')

    # HTML path
    chart_path = f'{streamlit_data_path}/Visualizations/{zone}/Non-Spatial-Visualizations/difficulty_info.html'

    # Show the path
    with open(chart_path, "r", encoding="utf-8") as f:
        chart_html = f.read()
    html(chart_html, height=1200, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q5.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)
    
    st.markdown('---')

# Question 6.1 function
def question_6_1(zone, df):

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

    # HTML path
    chart_path = f'{streamlit_data_path}/Visualizations/{zone}/Non-Spatial-Visualizations/time_distribution.html'

    # Show the path
    with open(chart_path, "r", encoding="utf-8") as f:
        chart_html = f.read()
    html(chart_html, height=1000, scrolling=False)

# Question 6.2 function
def question_6_2(zone, df):

    st.markdown('---')

    # Header
    st.markdown('#### Two Years Registered Tracks Comparison between Months')

    # HTML path
    chart_path = f'{streamlit_data_path}/Visualizations/{zone}/Non-Spatial-Visualizations/two_years_month_comp.html'

    # Show the path
    with open(chart_path, "r", encoding="utf-8") as f:
        chart_html = f.read()
    html(chart_html, height=550, scrolling=False)

# Question 6.3 function
def question_6_3(zone, df):

    st.markdown('---')

    # Header
    st.markdown('#### Two Years Registered Tracks Comparison between Weekdays')

    # HTML path
    chart_path = f'{streamlit_data_path}/Visualizations/{zone}/Non-Spatial-Visualizations/two_years_weekday_comp.html'

    # Show the path
    with open(chart_path, "r", encoding="utf-8") as f:
        chart_html = f.read()
    html(chart_html, height=550, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q6.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Question 7 function
def question_7(zone, df):

    # Header
    st.header('Weather and Registered Tracks Relation depending on one Year')

    st.markdown('---')

    # Introduction to the visualization
    with open(f'{streamlit_data_path}/Text/General/intro_q7.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)

    st.markdown('---')

    # HTML path
    chart_path = f'{streamlit_data_path}/Visualizations/{zone}/Non-Spatial-Visualizations/weather_calendar.html'

    # Show the path
    with open(chart_path, "r", encoding="utf-8") as f:
        chart_html = f.read()
    html(chart_html, height=700, scrolling=False)

    st.markdown('---')

    # Print the information
    with open(f'{streamlit_data_path}/Text/{zone}/answer_q7.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    st.markdown(content)

    st.markdown('---')

# Function to create the q&a page for the zone
def zone_questions_and_answers(zone, df):
    
    st.subheader("Questions and Answers")
    st.markdown('---')

    # Write introduction
    with open(f'{streamlit_data_path}/Text/General/intro_questions.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.markdown(content)

    st.markdown("---")

    # Question 1
    with st.status("Which are the most commonly used start and end points in each zone, and which route segments are the most frequented? Can we identify areas where people frequently stop?", expanded=False):
        
        # Call the function
        question_1(zone, df)

    st.markdown("---")

    # Question 2
    with st.status("Are some sections avoided depending on difficulty?"):

        # Call the function
        question_2(zone, df)

    st.markdown("---")

    # Question 3
    with st.status("Does the usage of certain paths change over time?"):

        # Call the function
        question_3(zone, df)

    st.markdown("---")

    # Question 4
    with st.status("Are some paths used depending on the weather conditions?"):

        # Call the function
        question_4(zone, df)

    st.markdown("---")

    # Question 5
    with st.status("Can we correlate the perceived difficulty with different quantitative variables? What is the distribution of this variables?"):

        # Call the function
        question_5(zone, df)

    st.markdown("---")

    # Question 6
    with st.status("How has the number of recorded routes evolved throughout the year, and which periods show the highest activity?"):

        # Call the functions
        question_6_1(zone, df)
        question_6_2(zone, df)
        question_6_3(zone, df)

    st.markdown("---")
    
    # Question 7
    with st.status("What is the relationship between weather conditions and the number of recorded routes?"):

        # Call the function
        question_7(zone, df)

# Returns the track ID visualizations
def track_visualizations(zone, df, track_id):

    # Obtain the single track visualizations paths
    map_path = f'{streamlit_data_path}/Visualizations/{zone}/Single-Tracks-Visualizations/{track_id}_map.html'
    chart_path = f'{streamlit_data_path}/Visualizations/{zone}/Single-Tracks-Visualizations/{track_id}_chart.html'

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

        # Explain the visualization
        with open(f'{streamlit_data_path}/Text/General/intro_individual_vis1.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        st.markdown(content)

        # Show the visualization
        with open(chart_path, "r", encoding="utf-8") as f:
            chart_html = f.read()
        html(chart_html, height=400, scrolling=False)

        st.markdown("---")

        # Insert title
        st.subheader(f'Path of the Track {track_id}')

        # Write the introduction
        with open(f'{streamlit_data_path}/Text/General/intro_individual_vis2.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        st.markdown(content)

        # Create the map
        with open(map_path, "r", encoding="utf-8") as f:    # Read the html
            map_html = f.read()

        # Show the map
        html(map_html, height=800, scrolling=False)

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

