import pandas as pd
import os
import altair as alt
from spatial import *
from non_spatial import *

# Function to create and save the edges map given some instructions
def create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, name_df, name_column, filter_column, name_html, visualizations_path):

    # Create the path, and check if it exists
    path = os.path.join(visualizations_path, name_html)
    if not os.path.exists(path):

        # Read the edges dataframe
        edges_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Data-Frames/Edges-Dataframes/{name_df}')

        # Filter the tracks info dataframe using the column, and also filter the waypoints df
        filtered_tracks_df = tracks_info_df[tracks_info_df[name_column] == filter_column]
        list_filtered_tracks = filtered_tracks_df['track_id'].unique().tolist()
        filtered_waypoints = waypoints_df[waypoints_df['track_id'].isin(list_filtered_tracks)]

        # Generate the edges map using the function and save it
        edges_map = create_edges_map(edges_df, zone, filtered_tracks_df, filtered_waypoints)       # Create the map
        edges_map.save(path)

# Function to create all the edges maps
def create_all_edges_maps(zone, data_path, tracks_info_df, waypoints_df, all_edges_df, visualizations_path):

    # General edges map
    all_edges_path = os.path.join(visualizations_path, 'all_edges_map.html')    # Generate path 
    if not os.path.exists(all_edges_path):      # Check if it exists
        all_edges_map = create_edges_map(all_edges_df, zone, tracks_info_df, waypoints_df)      # Create the map
        all_edges_map.save(all_edges_path)  

    # Difficulties
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'difficulty_easy.csv', 'difficulty', 'Easy', 'easy_edges.html', visualizations_path)
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'difficulty_moderate.csv', 'difficulty', 'Moderate', 'moderate_edges.html', visualizations_path)
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'difficulty_difficult.csv', 'difficulty', 'Difficult', 'difficult_edges.html', visualizations_path)
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'difficulty_very_difficult.csv', 'difficulty', 'Very difficult', 'very_difficult_edges.html', visualizations_path)

    # Weather conditions
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'weather_clear.csv', 'weather_condition', 'Clear', 'clear_edges.html', visualizations_path)
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'weather_cloudy.csv', 'weather_condition', 'Cloudy', 'cloudy_edges.html', visualizations_path)
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'weather_drizzle.csv', 'weather_condition', 'Drizzle', 'drizzle_edges.html', visualizations_path)
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'weather_rain.csv', 'weather_condition', 'Rain', 'rain_edges.html', visualizations_path)
    create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, 'weather_snow.csv', 'weather_condition', 'Snow', 'snow_edges.html', visualizations_path)

    # Years
    for year in tracks_info_df['year'].unique().tolist():
        create_and_save_edges_map(zone, data_path, tracks_info_df, waypoints_df, f'year_{year}.csv', 'year', year, f'{year}_edges.html', visualizations_path)

# Function to create all the non-spatial visualizations
def create_non_spatial_visualizations(zone, tracks_info_df, weather_df, visualizations_path):

    # Only process time distribution if does not exist
    time_dist_path = os.path.join(visualizations_path, 'time_distribution.html')

    if not os.path.exists(time_dist_path):

        # Time distribution call
        year_bar_chart, month_bar_chart, all_dates_line = time_distribution(tracks_info_df)

        # Sizes and titles
        year_bar_chart = year_bar_chart.properties(width=415, height=400, title='Registered tracks per year')
        month_bar_chart = month_bar_chart.properties(width=415, height=400, title='Registered tracks per month')
        all_dates_line = all_dates_line.properties(width=900, height=400, title='Evolution of registered tracks through the years')

        # Distribution
        time_distribution_chart = alt.vconcat(alt.hconcat(year_bar_chart, month_bar_chart), all_dates_line)
        time_distribution_chart.save(time_dist_path)

    # Check if it exist
    two_years_month_path = os.path.join(visualizations_path, 'two_years_month_comp.html')

    if not os.path.exists(two_years_month_path):

        # Two years comparison
        two_years_month_chart = two_years_month_comparison(tracks_info_df)

        # Size and title
        two_years_month_chart = two_years_month_chart.properties(width=900, height=400, title='Two years registered tracks comparison between months')

        # Save it
        two_years_month_chart.save(two_years_month_path)

    # Check if it exist
    two_years_weekday_path = os.path.join(visualizations_path, 'two_years_weekday_comp.html')

    if not os.path.exists(two_years_weekday_path):

        # Two years comparison
        two_years_weekday_chart = two_years_weekday_comparison(tracks_info_df)

        # Size and title
        two_years_weekday_chart = two_years_weekday_chart.properties(width=900, height=400, title='Two years registered tracks comparison between weekdays')

        # Save it
        two_years_weekday_chart.save(two_years_weekday_path)

    # Check if it exist
    difficulty_path = os.path.join(visualizations_path, 'difficulty_info.html')

    if not os.path.exists(difficulty_path):

        # Obtain the charts
        difficulty_bars, min_max_lines, scatter_grid = difficulty_info(tracks_info_df)

        # Sizes and titles
        difficulty_bars = difficulty_bars.properties(width=300, height=300, title='Total registered tracks per difficulty')

        # Distribution
        difficulty_info_chart = alt.hconcat(alt.vconcat(difficulty_bars, min_max_lines), scatter_grid)
        difficulty_info_chart.save(difficulty_path)

    # Check if it exists
    weather_path = os.path.join(visualizations_path, 'weather_calendar.html')

    if not os.path.exists(weather_path):

        # Obtain visualizations
        pie_chart, scatter_plot, calendar = calendar_weather(tracks_info_df, weather_df)

        # Sizes and titles
        pie_chart = pie_chart.properties(width=300, height=300, title='Weather condition registered tracks distribution')
        scatter_plot = scatter_plot.properties(width=500, height=300, title='Registered tracks depending on the mean temperature')
        calendar = calendar.properties(width=900, height=200, title='Calendar with the registered tracks per day and weather condition')

        # Distribution and save it
        weather_chart = alt.vconcat(alt.hconcat(pie_chart, scatter_plot), calendar)
        weather_chart.save(weather_path)

# Function to create a single track visualizations
def create_single_track_vis(zone, data_path, track_id, tracks_info_df, all_edges_df, waypoints_df, visualizations_path):

    # Create paths to save the html
    map_html_path = os.path.join(visualizations_path, f'{track_id}_map.html')
    chart_html_path = os.path.join(visualizations_path, f'{track_id}_chart.html')

    # Read all the track's dataframes
    track_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Tracks-Output/All-Tracks/{track_id}.csv')
    track_km_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Tracks-Output/Partial-Km/{track_id}.csv')
    track_pace_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Tracks-Output/Partial-Pace/{track_id}.csv')
    track_edges_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Tracks-Output/Partial-Edges/{track_id}.csv')

    # Create the track map - if the path does not exist
    if not os.path.exists(map_html_path):
        track_map = create_track_map(track_id, tracks_info_df, all_edges_df, waypoints_df, track_df, track_km_df, track_pace_df, track_edges_df)
        track_map.save(map_html_path)

    # Create the elevation profile - if the path does not exist
    if not os.path.exists(chart_html_path):
        track_chart = elevation_profile_and_pace_bars(track_df, track_km_df)
        track_chart = track_chart.properties(width=900)
        track_chart.save(chart_html_path)

# Main function
def main_save_visualizations(zone):
    
    # Define the data path
    data_path = '../../Data/Processing-Data'

    # Read all the needed paths
    tracks_info_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Data-Frames/tracks_info.csv')
    weather_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Data-Frames/weather.csv')
    waypoints_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Data-Frames/waypoints.csv')
    all_edges_df = pd.read_csv(f'{data_path}/{zone}/Output-Data/Data-Frames/Edges-Dataframes/all_edges.csv')

    # Create a visualizations directory if not created - inside the streamlit directory
    visualizations_path = f'../Streamlit/Data/Visualizations/{zone}'
    os.makedirs(visualizations_path, exist_ok=True)

    # Create the non spatial visualizations path
    non_spatial_vis_path = os.path.join(visualizations_path, 'Non-Spatial-Visualizations')
    os.makedirs(non_spatial_vis_path, exist_ok=True)

    # Create the maps visualizations path
    maps_vis_path = os.path.join(visualizations_path, 'Edges-Maps-Visualizations')
    os.makedirs(maps_vis_path, exist_ok=True)

    # Create the single tracks path directory if not created
    single_tracks_vis_path = os.path.join(visualizations_path, 'Single-Tracks-Visualizations')
    os.makedirs(single_tracks_vis_path, exist_ok=True)

    # Create all edges maps
    create_all_edges_maps(zone, data_path, tracks_info_df, waypoints_df, all_edges_df, maps_vis_path)

    # Create all non-spatial visualizations
    create_non_spatial_visualizations(zone, tracks_info_df, weather_df, non_spatial_vis_path)

    # Create all the single tracks visualizations
    for track_id in tracks_info_df['track_id'].unique().tolist():
        create_single_track_vis(zone, data_path, track_id, tracks_info_df, all_edges_df, waypoints_df, single_tracks_vis_path)

# Call the main function for the three zones
print('El Canigó')
main_save_visualizations('canigo')
print('El Matagalls')
main_save_visualizations('matagalls')
print('La Vall Ferrera')
main_save_visualizations('vallferrera')
