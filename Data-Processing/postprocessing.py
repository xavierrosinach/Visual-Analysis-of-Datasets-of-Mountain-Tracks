import geopandas as gpd
import pandas as pd
import os
import json
from geopy.distance import geodesic
from pandas.errors import SettingWithCopyWarning
from shapely.geometry import LineString
from datetime import datetime
import requests
import numpy as np
import warnings
from sklearn.cluster import KMeans
import ast

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="Could not find the number of physical cores")
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)

# Dictionary with the center coordinates
center_coords_dict = {"canigo": (2.5, 42.5), "matagalls": (2.4, 41.825), "vallferrera": (1.35, 42.6), "exemple": (2.4, 41.825)}

# Generates the edges dataframe
def generate_edges_df(osm_data_path):

    edges_df = gpd.read_file(os.path.join(osm_data_path, 'edges.shp'))      # Load the edges dataframe with geopandas
    edges_df = edges_df[['u','v','geometry']]       # Select only needed columns

    # Apply order to u and v to avoid duplicated edges
    edges_df[['u', 'v']] = edges_df.apply(lambda row: sorted([row['u'], row['v']]), axis=1, result_type='expand')   # Apply order
    edges_df = edges_df.drop_duplicates(subset=['u','v'])   # Drop duplicated values

    # Sort the columns depending on u, and create an edge id
    edges_df = edges_df.sort_values(by='u').reset_index(drop=True)
    edges_df['id'] = range(1, len(edges_df) + 1)
    
    # Reorder the dataframe
    edges_df = edges_df[['id','u','v','geometry']]

    return edges_df

# Processes the input dataframe
def process_inp_df(input_coords_df):

    # Create an identificator for each coordinate point
    input_coords_df['id'] = range(1, len(input_coords_df) + 1)

    # Create the next_lat and lext_lon
    input_coords_df['next_lat'] = input_coords_df['lat'].shift().fillna(input_coords_df['lat'].iloc[0])
    input_coords_df['next_lon'] = input_coords_df['lon'].shift().fillna(input_coords_df['lon'].iloc[0])

    # Calculate the elevation difference
    input_coords_df['elev_diff'] = round(input_coords_df['elev'].diff(), 2).fillna(0)

    # Calculate the distance between two coordinates
    input_coords_df['dist_diff'] = round(input_coords_df.apply(lambda row: geodesic((row['lat'], row['lon']), (row['next_lat'], row['next_lon'])).meters if pd.notnull(row['next_lat']) else 0, axis=1), 2)

    # Calculate the time difference - timestamps difference in miliseconds
    input_coords_df['time_diff'] = round(abs(input_coords_df['timestamp'].diff()) / 1000, 2).fillna(0)

    # Calculate the speed in m/s
    input_coords_df['speed'] = round(input_coords_df.apply(lambda row: (row['dist_diff'] / row['time_diff']) if row['time_diff'] != 0 else 0, axis=1), 2)

    # Calculate the pace as min/km
    input_coords_df['pace'] = round(input_coords_df.apply(lambda row: 1/(row['speed'] * 0.06) if row['speed']!=0 else 0, axis=1), 2)
    
    # Add the elapsed distance (in km), and the elapsed time (in minutes)
    input_coords_df['elap_dist'] = round(input_coords_df['dist_diff'].cumsum() / 1000, 2)
    input_coords_df['elap_time'] = round(input_coords_df['time_diff'].cumsum() / 60, 2)

    # Add the elapsed elevation gain as the cum sum of positive values
    input_coords_df['elap_elev_gain'] = round(input_coords_df['elev_diff'].where(input_coords_df['elev_diff'] > 0, 0).cumsum(), 2)

    # Obtain only the desired columns of the dataframe
    input_coords_df = input_coords_df[['id','lat','lon','elev','elev_diff','dist_diff','time_diff','speed','pace','elap_elev_gain','elap_dist','elap_time']]

    return input_coords_df

# Processes the FMM output result
def process_fmm_df(output_fmm_df, edges_df):

    # Merge the dataframes
    output_fmm_df = output_fmm_df.merge(edges_df, on=['u','v'])

    # Cut the dataframe, and only get the edge_id, and the cleaned coords
    output_fmm_df = output_fmm_df.rename(columns={'lat':'osm_lat','lon':'osm_lon'})[['id','osm_lat','osm_lon']]

    # Make sure that the edge at least appears more than 2 consecutive times
    output_fmm_df['group'] = (output_fmm_df['id'] != output_fmm_df['id'].shift()).cumsum()    # Detect groups
    group_sizes = output_fmm_df.groupby('group')['id'].transform('size')       # Get the size
    output_fmm_df['edge_id'] = output_fmm_df['id'].where(group_sizes >= 3)    # Obtain the column, and put Nan if the size is lower
    output_fmm_df['edge_id'] = output_fmm_df['edge_id'].ffill().bfill().astype(int)   # Full fill

    # Get the final df
    output_fmm_df = output_fmm_df[['edge_id','osm_lat','osm_lon']]

    return output_fmm_df

# Function to return the cleaned track coordinates given the track input data and the output of the FMM algorithm
def clean_track_coordinates(inp_json_path, out_csv_path, edges_df):

    # Load JSON data from the file
    with open(inp_json_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # Obtain the two dataframes
    input_coords_df = pd.DataFrame(json_data["coordinates"], columns=["lon", "lat", "elev", "timestamp"])
    output_fmm_df = pd.read_csv(out_csv_path)

    # Process the input dataframe with the created function
    input_coords_df = process_inp_df(input_coords_df)

    total_elev_gain = input_coords_df['elap_elev_gain'].iloc[-1]  # Allow from 0 to 5000 meters
    total_time = input_coords_df['elap_time'].iloc[-1]  # Allow from 60 to 720 minutes 
    total_dist = input_coords_df['elap_dist'].iloc[-1]  # Allow from 2 to 35 km
    avg_speed = input_coords_df['speed'].mean()     # Allow from 0.8 to 2.8 m/s

    if (total_time < 60) or (total_time > 720) or (total_dist < 2) or (total_dist > 35) or (avg_speed < 0.8) or (avg_speed > 2.8) or (total_elev_gain > 5000):
        return input_coords_df, False
    
    # Function to process the output FMM dataframe
    output_fmm_df = process_fmm_df(output_fmm_df, edges_df)
    
    # Merge the two dataframes to add the edges info
    merged_df = pd.concat([input_coords_df.reset_index(drop=True), output_fmm_df.reset_index(drop=True)], axis=1)

    return merged_df, True

# Creates a partial dataframe given the track kms
def create_km_partial_df(track_df):

    # Select the desired columns
    km_df = track_df[['id','elap_dist','elap_elev_gain','elap_time','speed','pace']].copy()

    # Create the column km
    km_df['km'] = km_df['elap_dist'].astype(int)

    # Group by km
    grouped = km_df.groupby('km')

    # Get the last km number and max distance
    last_km = km_df['km'].max()
    last_km_dist = round(track_df['elap_dist'].iloc[-1] - last_km, 2)

    # Aggregate
    agg_df = grouped.agg(avg_speed=('speed', 'mean'),
                         avg_pace=('pace', 'mean'),
                         elap_time=('elap_time', lambda x: round(x.max(), 2)),
                         elap_dist=('elap_dist', lambda x: round(x.max() / 1000, 2)),
                         elap_elev_gain=('elap_elev_gain', lambda x: round(x.max(), 2)),
                         min_km_id=('id', 'min'),
                         max_km_id=('id', 'max')).reset_index()

    # Edit columns
    agg_df['max_km_id'] = agg_df.apply(lambda row: row['max_km_id'] + 1 if row['km'] != last_km else row['max_km_id'], axis=1).astype(int)      # Fix max_km_id (+1 except for the last)
    agg_df['dist'] = agg_df['km'].apply(lambda km: 1 if km != last_km else last_km_dist)       # Fix total_km_dist (1 except for the last)
    agg_df['avg_speed'] = round(agg_df['avg_speed'], 2)         # Round averages
    agg_df['avg_pace'] = round(agg_df['avg_pace'], 2)           # Round averages

    # Create an empty row for geometry
    agg_df['geometry'] = None

    # Given the columns of max and min id, get the geometry
    for index, row in agg_df.iterrows():
        coords_subset = track_df[(track_df['id'] >= row['min_km_id']) & (track_df['id'] <= row['max_km_id'])]
        line = LineString(zip(coords_subset['lon'], coords_subset['lat']))
        agg_df.at[index, 'geometry'] = line

    # Calculate the time difference and elevation gain difference
    agg_df['time'] = round(agg_df['elap_time'].diff(), 2).fillna(agg_df['elap_time'].iloc[0])
    agg_df['elev_gain'] = round(agg_df['elap_elev_gain'].diff(), 2).fillna(agg_df['elap_elev_gain'].iloc[0])

    return agg_df[['km','avg_speed','avg_pace','time','dist','elap_elev_gain','geometry']]    # Return a cutted df

# Creates a partial dataframe of the track depending on 4 average pace zones
def create_pace_partial_df(track_df):
    # Select only pace rows and make an explicit copy to avoid SettingWithCopyWarning
    pace_df = track_df[['id', 'pace']].copy()

    # Create pace level categories using quartiles
    pace_df['pace_level'] = pd.qcut(pace_df['pace'], 4, labels=[1, 2, 3, 4]).astype(int)

    # Avoid outliers in the pace level column
    pace_df['group'] = (pace_df['pace_level'] != pace_df['pace_level'].shift()).cumsum()        # Detect groups of consecutive identical pace levels
    group_sizes = pace_df.groupby('group')['pace_level'].transform('size')      # Calculate group sizes
    pace_df.loc[group_sizes < 5, 'pace_level'] = np.nan         # Set pace_level to NaN for small groups (< 5), then forward fill
    pace_df['pace_level'] = pace_df['pace_level'].ffill().bfill().astype(int)

    # Group by pace levels
    pace_df['group_2'] = (pace_df['pace_level'] != pace_df['pace_level'].shift()).cumsum()
    pace_df = pace_df.groupby('group_2').first().reset_index()[['id', 'pace_level']]

    # Reset the name of id to min_id, and calculate the max id column as the next 
    pace_df = pace_df.rename(columns={'id':'min_id'})
    pace_df['max_id'] = pace_df['min_id'].shift(-1).fillna(track_df['id'].max()).astype(int)

    # Create empty columns
    pace_df['elap_dist'] = None
    pace_df['elap_time'] = None
    pace_df['elap_elev_gain'] = None
    pace_df['avg_pace'] = None
    pace_df['avg_speed'] = None
    pace_df['geometry'] = None

    # Add the geometry column
    for index, row in pace_df.iterrows():

        # Create a subset and a linestring of coords
        coords_subset = track_df[(track_df['id'] >= row['min_id']) & (track_df['id'] <= row['max_id'])]
        line = LineString(zip(coords_subset['lon'], coords_subset['lat']))
        pace_df.at[index, 'geometry'] = line

        # The other metrics dataframe consists on getting rid of one column of the previous
        if index == pace_df.index[-1]: 
            metrics_subset = coords_subset.copy()
        else:
            metrics_subset = track_df[(track_df['id'] >= row['min_id']) & (track_df['id'] <= (row['max_id']-1))]

        # Get the vlaues
        pace_df.at[index, 'elap_dist'] = round(metrics_subset['elap_dist'].max(), 2)
        pace_df.at[index, 'elap_time'] = round(metrics_subset['elap_time'].max(), 2)
        pace_df.at[index, 'elap_elev_gain'] = round(metrics_subset['elap_elev_gain'].max(), 2)
        pace_df.at[index, 'avg_pace'] = round(metrics_subset['pace'].mean(), 2)
        pace_df.at[index, 'avg_speed'] = round(metrics_subset['speed'].mean(), 2)
    
    # Calculate the distance, time difference and elevation gain difference
    pace_df['dist'] = round(pace_df['elap_dist'].diff(), 2).fillna(pace_df['elap_dist'].iloc[0])
    pace_df['time'] = round(pace_df['elap_time'].diff(), 2).fillna(pace_df['elap_time'].iloc[0])
    pace_df['elev_gain'] = round(pace_df['elap_elev_gain'].diff(), 2).fillna(pace_df['elap_elev_gain'].iloc[0])

    return pace_df[['avg_speed','avg_pace','time','dist','elev_gain','geometry']]

# Creates a partial dataframe for the edges - metrics for each edge
def create_edges_partial_df(track_df):

    # Set a subset of the dataframe
    edges_df = track_df[['id','edge_id']]

    # Group by consecutive edge_id values
    edges_df = edges_df.copy()      # Set a copy to avoid warnings
    edges_df['group'] = (edges_df['edge_id'] != edges_df['edge_id'].shift()).cumsum()
    edges_df = edges_df.groupby('group').first().reset_index()[['id', 'edge_id']]

    # Reset the name of id to min_id, and calculate the max id column as the next 
    edges_df = edges_df.rename(columns={'id':'min_id'})
    edges_df['max_id'] = edges_df['min_id'].shift(-1).fillna(track_df['id'].max()).astype(int)

    # Create empty columns
    edges_df['elap_dist'] = None
    edges_df['elap_time'] = None
    edges_df['elap_elev_gain'] = None
    edges_df['avg_pace'] = None
    edges_df['avg_speed'] = None
    edges_df['geometry'] = None

    # Add the geometry column
    for index, row in edges_df.iterrows():

        # Create a subset and a linestring of coords
        coords_subset = track_df[(track_df['id'] >= row['min_id']) & (track_df['id'] <= row['max_id'])]
        line = LineString(zip(coords_subset['lon'], coords_subset['lat']))
        edges_df.at[index, 'geometry'] = line

        # The other metrics dataframe consists on getting rid of one column of the previous
        if index == edges_df.index[-1]: 
            metrics_subset = coords_subset.copy()
        else:
            metrics_subset = track_df[(track_df['id'] >= row['min_id']) & (track_df['id'] <= (row['max_id']-1))]

        # Get the vlaues
        edges_df.at[index, 'elap_dist'] = round(metrics_subset['elap_dist'].max(), 2)
        edges_df.at[index, 'elap_time'] = round(metrics_subset['elap_time'].max(), 2)
        edges_df.at[index, 'elap_elev_gain'] = round(metrics_subset['elap_elev_gain'].max(), 2)
        edges_df.at[index, 'avg_pace'] = round(metrics_subset['pace'].mean(), 2)
        edges_df.at[index, 'avg_speed'] = round(metrics_subset['speed'].mean(), 2)

    # Calculate the distance, time difference and elevation gain difference
    edges_df['dist'] = round(edges_df['elap_dist'].diff(), 2).fillna(edges_df['elap_dist'].iloc[0])
    edges_df['time'] = round(edges_df['elap_time'].diff(), 2).fillna(edges_df['elap_time'].iloc[0])
    edges_df['elev_gain'] = round(edges_df['elap_elev_gain'].diff(), 2).fillna(edges_df['elap_elev_gain'].iloc[0])

    return edges_df[['edge_id','avg_speed','avg_pace','time','dist','elev_gain','geometry']]

# Given a date in string format, returns other metrics
def obtain_date(input_date):

    # Clean the input date - initially it is in catalan, replace strings
    input_date = input_date.replace("de gener", "January").replace("de febrer", "February").replace("de març", "March").replace("d’abril", "April").replace("d'abril", "April").replace("de maig", "May")
    input_date = input_date.replace("de juny", "June").replace("de juliol", "July").replace("d’agost", "August").replace("d'agost", "August").replace("de setembre", "September").replace("d’octubre", "October")
    input_date = input_date.replace("d'octubre", "October").replace("de novembre", "November").replace("de desembre", "December")

    # Proceed with the conversion
    date = input_date.replace(" de ", " ")  # Remove the extra 'de'
    date = pd.to_datetime(datetime.strptime(date.strip(), "%d %B %Y").strftime("%d/%m/%Y"), dayfirst=True).date()   # Convert to datetime
    
    # Find the year, month, and weekday (first three leters)
    year = date.year
    month = date.strftime('%b')
    weekday = date.strftime('%a')
    
    # Map months to meteorological seasons
    season_map = {'Dec':'Win', 'Jan':'Win', 'Feb':'Win', 'Mar':'Spr', 'Apr':'Spr', 'May':'Spr', 'Jun':'Sum', 'Jul':'Sum', 'Aug':'Sum', 'Sep':'Aut', 'Oct':'Aut', 'Nov':'Aut'}
    season = season_map[month]

    return date, month, year, season, weekday

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
    
    url = (f"https://archive-api.open-meteo.com/v1/archive?"    # Url with the information
            f"latitude={lat}&longitude={lon}"
            f"&start_date={start_date}&end_date={end_date}"
            f"&daily=temperature_2m_min,temperature_2m_max,weathercode"
            f"&timezone=auto")

    data = requests.get(url).json()     # The request to json format

    df = pd.DataFrame({"date": data["daily"]["time"],   # Result to dataframe
                        "min_temp": data["daily"]["temperature_2m_min"],
                        "max_temp": data["daily"]["temperature_2m_max"],
                        "weather_code": data["daily"]["weathercode"]})
    
    df['weather_condition'] = df['weather_code'].map(weather_mapping)

    return df[['date', 'min_temp', 'max_temp', 'weather_condition']]

# Part 1 of the postprocessing - obtains the routes information
def postprocessing_part1(input_path, osm_path, output_path, dataframes_path, fmm_out_path):
    
    # Obtain the edges dataframe
    if os.path.exists(os.path.join(dataframes_path, 'edges.csv')):
        edges_df = pd.read_csv(os.path.join(dataframes_path, 'edges.csv'))
    else:
        edges_df = generate_edges_df(osm_path)
        edges_df.to_csv(os.path.join(dataframes_path, 'edges.csv'), index=False)

    # Read the fmm output configuration dataframe
    fmm_config_df = pd.read_csv(os.path.join(dataframes_path, 'fmm_config.csv'))

    # Create a tracks output directory to store all the information
    tracks_out_path = os.path.join(output_path, 'Tracks-Output')
    os.makedirs(tracks_out_path, exist_ok=True)

    # Obtain the discard dataframe
    disc_path = os.path.join(dataframes_path, 'discarded.csv')
    disc_df = pd.read_csv(disc_path)

    # Four different directories inside the tracks output
    all_tracks_path = os.path.join(tracks_out_path, 'All-Tracks')
    os.makedirs(all_tracks_path, exist_ok=True)
    partial_km_path = os.path.join(tracks_out_path, 'Partial-Km')
    os.makedirs(partial_km_path, exist_ok=True)
    partial_pace_path = os.path.join(tracks_out_path, 'Partial-Pace')
    os.makedirs(partial_pace_path, exist_ok=True)
    partial_edges_path = os.path.join(tracks_out_path, 'Partial-Edges')
    os.makedirs(partial_edges_path, exist_ok=True)

    # Read the dataframe
    if os.path.exists(os.path.join(dataframes_path, 'tracks_info.csv')):
        track_info_df = pd.read_csv(os.path.join(dataframes_path, 'tracks_info.csv'))
    
    else:
        # Create an empty dataframe, we will iterate to append information for each track
        track_info_df = pd.DataFrame(columns=['track_id','user','title','url','difficulty','date','month','year','season','weekday','total_time',
                                            'total_distance','average_speed','average_pace','elevation_gain','min_temp','max_temp','weather_condition',
                                            'first_coordinate','last_coordinate','start_zone','finish_zone','geometry'])
        track_info_df.to_csv(os.path.join(dataframes_path, 'tracks_info.csv'), index=False)

    # Obtain a list with the already processed tracks, the tracks in track_info_df, and the discarded files with error 7
    processed_tracks = list(set(track_info_df['track_id'].unique().tolist() + disc_df[disc_df['error_type'] == 7]['track_id'].unique().tolist()))

    # Tracks to proceed
    len_df = len(fmm_config_df) - len(processed_tracks)
    index = 1
    
    # For each track, proceed
    for track_id in fmm_config_df['track_id'].unique().tolist():

        if int(track_id) not in processed_tracks:

            print(f'Processing track {track_id} ({index}/{len_df})', end='\r', flush=True)
            index += 1

            # Track path information
            inp_json_path = os.path.join(input_path, str(track_id)+'.json')
            out_csv_path = os.path.join(fmm_out_path, str(track_id)+'.csv')

            try:
                # Obtain the all track dataframe with the input json and the cleaned coordinates
                all_track_df, valid_track = clean_track_coordinates(inp_json_path, out_csv_path, edges_df)

                if not valid_track:
                    disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[7]})], ignore_index=True)
                    disc_df.to_csv(disc_path, index=False)
                    continue

                else:
                    # Save the track df
                    all_track_df.to_csv(os.path.join(all_tracks_path, str(track_id)+'.csv'), index=False)

                    # Create the three partials dataframes
                    km_partial_df = create_km_partial_df(all_track_df)
                    pace_partial_df = create_pace_partial_df(all_track_df)
                    edges_partial_df = create_edges_partial_df(all_track_df)

                    # Save the partial df
                    km_partial_df.to_csv(os.path.join(partial_km_path, str(track_id)+'.csv'), index=False)
                    pace_partial_df.to_csv(os.path.join(partial_pace_path, str(track_id)+'.csv'), index=False)
                    edges_partial_df.to_csv(os.path.join(partial_edges_path, str(track_id)+'.csv'), index=False)
            
            except:
                disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[7]})], ignore_index=True)
                disc_df.to_csv(disc_path, index=False)
                continue

            # Load JSON data from the file
            with open(inp_json_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

            # List to store the track information while we are getting it
            track_information = []

            # Track id, and other information
            track_information.extend([track_id, json_data['user'], json_data['title'], json_data['url'], json_data['difficulty']])

            # Apply the function to know the date correctly and the other metrics
            date, month, year, season, weekday = obtain_date(json_data['date-up'])

            # Discard if the track is older than 2012 (only in canigo and vallferrera)
            if year >= 2012:

                # Add all this information into the list
                track_information.extend([date, month, year, season, weekday])

                # Extend the list with the track metrics (calculated in the dataframe before)
                track_information.extend([all_track_df['elap_time'].iloc[-1],  # Total time
                                        all_track_df['elap_dist'].iloc[-1],  # Total distance
                                        round(all_track_df['speed'].mean(), 2),  # Average speed
                                        round(all_track_df['pace'].mean(), 2),   # Average pace
                                        all_track_df[all_track_df['elev_diff'] > 0]['elev_diff'].sum()])    # Elevation gain

                # For the weather data, insert None data
                track_information.extend([None, None, None])

                # Insert the first and the last coordinates, also None data for the zone
                track_information.extend([(all_track_df['lat'].iloc[0], all_track_df['lon'].iloc[0]),
                                        (all_track_df['lat'].iloc[-1], all_track_df['lon'].iloc[-1]),
                                        None, None])

                # Insert the geometry
                track_information.append(LineString(zip(all_track_df['lat'], all_track_df['lon'])))
                
                # # Add the track information into the dataframe
                track_info_df.loc[len(track_info_df)] = track_information
                track_info_df.to_csv(os.path.join(dataframes_path, 'tracks_info.csv'), index=False)

            else:
                disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[7]})], ignore_index=True)
                disc_df.to_csv(disc_path, index=False)   
                continue

# Part 2 of the postprocessing - inputs the weather information and the starting and ending zones
def postprocessing_part2(zone, dataframes_path):

    # Read the tracks info dataframe
    tracks_info_path = os.path.join(dataframes_path, 'tracks_info.csv')
    tracks_info_df = pd.read_csv(tracks_info_path)

    # Obtain the weather information dataframe
    weather_df = obtain_weather_dataframe(tracks_info_df['date'].min(), tracks_info_df['date'].max(), zone)

    # Drop the weather information columns from the initial dataframe
    tracks_info_df = tracks_info_df.drop(columns=['min_temp','max_temp','weather_condition'])

    # Merge dataframes, and reorder the final one with the desired order
    tracks_info_df = tracks_info_df.merge(weather_df, on='date')
    
    # Obtain ten clusters to identify start and ending zones
    tracks_info_df['first_coordinate'] = tracks_info_df['first_coordinate'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)   # String to tuple
    tracks_info_df['last_coordinate'] = tracks_info_df['last_coordinate'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    tracks_info_df[['first_lat', 'first_lon']] = pd.DataFrame(tracks_info_df['first_coordinate'].tolist(), index=tracks_info_df.index)          # Split into separate lat and lon columns
    tracks_info_df[['last_lat', 'last_lon']] = pd.DataFrame(tracks_info_df['last_coordinate'].tolist(), index=tracks_info_df.index)

    # Apply KMeans for the starting zone
    kmeans = KMeans(n_clusters=10, random_state=42)
    tracks_info_df['start_zone'] = kmeans.fit_predict(tracks_info_df[['first_lat', 'first_lon']])
    tracks_info_df['finish_zone'] = kmeans.fit_predict(tracks_info_df[['last_lat', 'last_lon']])

    # Reorder the dataframe
    tracks_info_df = tracks_info_df[['track_id','user','title','url','difficulty','date','month','year','season','weekday','total_time',
                                     'total_distance','average_speed','average_pace','elevation_gain','min_temp','max_temp','weather_condition',
                                     'first_coordinate','last_coordinate','start_zone','finish_zone','geometry']]

    # Save the tracks info dataframe to the desired path
    tracks_info_df.to_csv(tracks_info_path, index=False)

# Main postprocessing function
def main_postprocessing(data_path, zone):

    # Obtain all the paths
    zone_path = os.path.join(data_path, zone)
    input_path = os.path.join(zone_path, 'Input-Data')
    osm_path = os.path.join(zone_path, 'OSM-Data')
    output_path = os.path.join(zone_path, 'Output-Data')
    dataframes_path = os.path.join(output_path, 'Data-Frames')
    fmm_out_path = os.path.join(output_path, 'FMM-Output')

    # Proceed with the first part and second of the postprocessing
    postprocessing_part1(input_path, osm_path, output_path, dataframes_path, fmm_out_path)
    postprocessing_part2(zone, dataframes_path)
    