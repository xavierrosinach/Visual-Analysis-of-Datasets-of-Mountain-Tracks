import pandas as pd
import os
import numpy as np
import geopandas as gpd
from datetime import datetime
import requests

center_coords_dict = {"canigo": (2.5, 42.5), "matagalls": (2.4, 41.825), "vallferrera": (1.35, 42.6)}

# Converts the string date into a correct date
def convert_date(date):

    # Replace types of appostrofes
    date = date.replace("de gener", "January")
    date = date.replace("de febrer", "February")
    date = date.replace("de març", "March")
    date = date.replace("d’abril", "April")
    date = date.replace("d'abril", "April")
    date = date.replace("de maig", "May")
    date = date.replace("de juny", "June")
    date = date.replace("de juliol", "July")
    date = date.replace("d’agost", "August")
    date = date.replace("d'agost", "August")
    date = date.replace("de setembre", "September")
    date = date.replace("d’octubre", "October")
    date = date.replace("d'octubre", "October")
    date = date.replace("de novembre", "November")
    date = date.replace("de desembre", "December")

    # Remove the extra "de"
    date = date.replace(" de ", " ")

    # Convert to datetime
    date = datetime.strptime(date.strip(), "%d %B %Y")

    return date.strftime("%d/%m/%Y")

# Function to obtain the weather information of a given zone from one date to another
def obtain_weather_dataframe(start_date, end_date, zone):

    # Transform the start and the end dates
    start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')

    # Obtain the center cords
    center_cords = center_coords_dict[zone]
    lon = center_cords[0]
    lat = center_cords[1]

    # Convert weather code to a readable condition
    weather_mapping = {0: "Clear", 1: "Clear",          # The library has more weather conditions, but we define less groups
                       2: "Cloudy", 3: "Cloudy",
                       45: "Fog", 48: "Fog",
                       51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
                       61: "Rain", 63: "Rain", 65: "Rain", 80: "Rain", 81: "Rain", 82: "Rain",
                       71: "Snow", 73: "Snow", 75: "Snow",
                       95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm"}
    
    # Url with the information
    url = (f"https://archive-api.open-meteo.com/v1/archive?"    
            f"latitude={lat}&longitude={lon}"
            f"&start_date={start_date}&end_date={end_date}"
            f"&daily=temperature_2m_min,temperature_2m_max,weathercode"
            f"&timezone=auto")

    # The request to json format
    data = requests.get(url).json()     

    # Result to dataframe
    df = pd.DataFrame({"date": data["daily"]["time"], "min_temp": data["daily"]["temperature_2m_min"], "max_temp": data["daily"]["temperature_2m_max"], "weather_code": data["daily"]["weathercode"]})
    
    # Map the wather condition since we want a readable one
    df['weather_condition'] = df['weather_code'].map(weather_mapping)

    # Convert to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Return ordered dataframe
    return df[['date', 'min_temp', 'max_temp', 'weather_condition']]

# Function to clean the tracks info
def clean_tracks_info(tracks_info_df, zone, cleaned_output_path):

    # Date treatment
    tracks_info_df['date_up'] = tracks_info_df['date_up'].apply(convert_date)

    # Obtain the month, weekday, and year (only 3 letters if month and weekday)
    tracks_info_df['date_up'] = pd.to_datetime(tracks_info_df['date_up'], format='%d/%m/%Y')
    tracks_info_df['year'] = tracks_info_df['date_up'].dt.year
    tracks_info_df['month'] = tracks_info_df['date_up'].dt.strftime('%b') 
    tracks_info_df['weekday'] = tracks_info_df['date_up'].dt.strftime('%a')
    
    # Map months to meteorological seasons
    season_map = {'Dec':'Win', 'Jan':'Win', 'Feb':'Win', 'Mar':'Spr', 'Apr':'Spr', 'May':'Spr', 'Jun':'Sum', 'Jul':'Sum', 'Aug':'Sum', 'Sep':'Aut', 'Oct':'Aut', 'Nov':'Aut'}
    tracks_info_df['season'] = tracks_info_df['month'].map(season_map)

    # Obtain the weather dataframe
    weather_df = obtain_weather_dataframe(tracks_info_df['date_up'].min(), tracks_info_df['date_up'].max(), zone)

    # Merge the two dataframes
    tracks_info_df = tracks_info_df.merge(weather_df, left_on='date_up', right_on='date').drop(columns='date')

    # For each track, obtain the first and the last coordinates
    for index, row in tracks_info_df.iterrows():

        # Read the track id
        track_df = pd.read_csv(os.path.join(cleaned_output_path, str(row['track_id']) + '.csv'))

        # Find the metrics
        first_lat = track_df['lat'].iloc[0]
        first_lon = track_df['lon'].iloc[0]
        last_lat = track_df['lat'].iloc[-1]
        last_lon = track_df['lon'].iloc[-1]

        # Add these values to the DataFrame
        tracks_info_df.at[index, 'first_lat'] = first_lat
        tracks_info_df.at[index, 'first_lon'] = first_lon
        tracks_info_df.at[index, 'last_lat'] = last_lat
        tracks_info_df.at[index, 'last_lon'] = last_lon

    return tracks_info_df

# Obtain the dates dataframe with the total tracks per date
def obtain_date_df(tracks_info_df):

    # Create the column date from the minimum date to the maximum date
    dates_df = pd.DataFrame({'date':pd.date_range(start=tracks_info_df['date_up'].min(), end=tracks_info_df['date_up'].max(), freq='D'), 'total_tracks':0})

    # Add information like the month, year, weekday, and season
    dates_df['year'] = dates_df['date'].dt.year
    dates_df['month'] = dates_df['date'].dt.strftime('%b') 
    dates_df['weekday'] = dates_df['date'].dt.strftime('%a')
    
    # Map months to meteorological seasons
    season_map = {'Dec':'Win', 'Jan':'Win', 'Feb':'Win', 'Mar':'Spr', 'Apr':'Spr', 'May':'Spr', 'Jun':'Sum', 'Jul':'Sum', 'Aug':'Sum', 'Sep':'Aut', 'Oct':'Aut', 'Nov':'Aut'}
    dates_df['season'] = dates_df['month'].map(season_map)

    # Count the total tracks per date
    dates_df['total_tracks'] = dates_df['date'].apply(lambda x: len(tracks_info_df[tracks_info_df['date_up'] == x]))

    # Create a column with the cumulative sum of total tracks to know the evolution
    dates_df['cumul_total_tracks'] = dates_df['total_tracks'].cumsum()

    # Create and return new DataFrame
    return dates_df

# Main visualisations preprocessing - to create the needed dataframes for the visualisations
def main_vis_prep(data_path, zone):

    # Obtain the zone path and the other paths to read all the information we need
    zone_path = os.path.join(data_path, zone)
    osm_data_path = os.path.join(zone_path, 'OSM-Data')
    output_path = os.path.join(zone_path, 'Output-Data')
    dataframes_path = os.path.join(output_path, 'Data-Frames')
    cleaned_output_path = os.path.join(output_path, 'Cleaned-Tracks')

    # Read the dataframes we will need
    tracks_info_df = pd.read_csv(os.path.join(dataframes_path, 'tracks_info.csv'))
    waypoints_df = pd.read_csv(os.path.join(dataframes_path, 'waypoints.csv'))

    # Create a directory 'Visualisations-Data-Frames' to store the needed dataframes in the output directory
    vis_df_path = os.path.join(output_path, 'Visualisations-Data-Frames')
    os.makedirs(vis_df_path, exist_ok=True)  

    # Clean the tracks info dataframe
    tracks_info_df = clean_tracks_info(tracks_info_df.copy(), zone, cleaned_output_path)
    tracks_info_df.to_csv(os.path.join(vis_df_path, 'extended_tracks_info.csv'), index=False)

    # Create the date df (only contains the total routes per date)
    dates_df = obtain_date_df(tracks_info_df)
    dates_df.to_csv(os.path.join(vis_df_path, 'dates.csv'), index=False)

main_vis_prep('../../Data-2', 'canigo')