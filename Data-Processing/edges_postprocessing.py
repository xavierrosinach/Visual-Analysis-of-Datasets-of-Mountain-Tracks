import geopandas as gpd
import pandas as pd
from pandas.errors import SettingWithCopyWarning
import os
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)

# Function to get the distance group
def apply_distance_group(distance_value):

    # Apply an id for the group
    if distance_value < 5:
        return 1        # [0 - 5)
    elif (distance_value >= 5) and (distance_value < 10):
        return 2        # [5 - 10)
    elif (distance_value >= 10) and (distance_value < 15):
        return 3        # [10 - 15)
    elif (distance_value >= 15) and (distance_value < 20):
        return 4        # [15 - 20)
    elif (distance_value >= 20) and (distance_value < 25):
        return 5        # [20 - 25)
    elif (distance_value >= 25) and (distance_value < 30):
        return 6        # [25 - 30)
    else:
        return 7        # [30 and more)
    
# Function to get the time group
def apply_time_group(time_value):

    # Apply an id for the group
    if time_value < 60:
        return 1        # [0 - 1h)
    elif (time_value >= 60) and (time_value < 120):
        return 2        # [1 - 2h)
    elif (time_value >= 120) and (time_value < 180):
        return 3        # [2 - 3h)
    elif (time_value >= 180) and (time_value < 240):
        return 4        # [3 - 4h)
    elif (time_value >= 240) and (time_value < 300):
        return 5        # [4 - 5h)
    elif (time_value >= 300) and (time_value < 360):
        return 6        # [5 - 6h)
    else:
        return 7        # (more than 6h)
    
# Function to get the pace group
def apply_pace_group(pace_value):

    # Apply an id for the group
    if pace_value < 20:
        return 1        # [0 - 20min/km)
    elif (pace_value >= 20) and (pace_value < 40):
        return 2        # [20 - 40min/km)
    elif (pace_value >= 40) and (pace_value < 60):
        return 3        # [40 - 60min/km)
    else:
        return 4        # (more than 60min/km)
    
# Function to get the elevation_gain group
def apply_elevation_group(elevation_value):

    # Apply an id for the group
    if elevation_value < 500:
        return 1        # [0 - 500m)
    elif (elevation_value >= 500) and (elevation_value < 1000):
        return 2        # [500 - 1000m)
    elif (elevation_value >= 1000) and (elevation_value < 1500):
        return 3        # [1000 - 1500m)
    elif (elevation_value >= 1500) and (elevation_value < 2000):
        return 4        # [1500 - 2000m)
    else:
        return 5        # (more than 2000m)
    
 # Custom binning into 4 levels for total_tracks and average_pace
def assign_level(value, min_val, max_val):
    # Define thresholds for 4 levels
    level_size = (max_val - min_val) / 4
    if value < min_val + level_size:
        return 1
    elif value < min_val + 2 * level_size:
        return 2
    elif value < min_val + 3 * level_size:
        return 3
    else:
        return 4
    
# Given a list of filtered tracks, gets the partial edges dataframe
def create_partial_edges_df(list_tracks, edges_df, partial_edges_path):

    # Create a copy
    partial_edges_df = edges_df[['id','geometry']].copy()

    # Create an empty list for the tracks, and another for the average pace
    partial_edges_df['list_tracks'] = [[] for _ in range(len(partial_edges_df))]
    partial_edges_df['list_avg_pace'] = [[] for _ in range(len(partial_edges_df))]

    # Set 'id' as index for faster lookup
    partial_edges_df.set_index('id', inplace=True)

    # Append the track into the list of tracks
    for track_id in list_tracks:

        # Read the csv
        track_df = pd.read_csv(os.path.join(partial_edges_path, str(track_id)+'.csv'))

        # For each row (edge)
        for index, row in track_df.iterrows():
            if row['edge_id'] in partial_edges_df.index:
                partial_edges_df.at[row['edge_id'], 'list_tracks'].append(track_id)
                partial_edges_df.at[row['edge_id'], 'list_avg_pace'].append(row['avg_pace'])

    # Reset index
    partial_edges_df.reset_index(inplace=True)

    # Create the total tracks column, and filter
    partial_edges_df['total_tracks'] = partial_edges_df['list_tracks'].map(len)
    partial_edges_df = partial_edges_df[partial_edges_df['total_tracks'] > 0]

    # Create the average pace column
    partial_edges_df['average_pace'] = round(partial_edges_df['list_avg_pace'].apply(lambda paces: np.mean(paces) if paces else None), 2)

    # Create total tracks and pace level categories using quartiles
    partial_edges_df['total_tracks_level'] = partial_edges_df['total_tracks'].apply(lambda x: assign_level(x, partial_edges_df['total_tracks'].min(), partial_edges_df['total_tracks'].max()))
    partial_edges_df['average_pace_level'] = partial_edges_df['average_pace'].apply(lambda x: assign_level(x, partial_edges_df['average_pace'].min(), partial_edges_df['average_pace'].max()))

    # Reorder the dataframe
    partial_edges_df = partial_edges_df[['id','average_pace','average_pace_level','total_tracks','total_tracks_level','list_tracks','geometry']]

    return partial_edges_df

# Main edges postprocessing
def main_edges_postprocessing(data_path, zone):

    # Obtain all the paths
    zone_path = os.path.join(data_path, zone)
    output_path = os.path.join(zone_path, 'Output-Data')
    dataframes_path = os.path.join(output_path, 'Data-Frames')

    # Read needed dataframes
    tracks_info_path = os.path.join(dataframes_path, 'tracks_info.csv')
    tracks_info_df = pd.read_csv(tracks_info_path)

    # Read the edges dataframe
    edges_df = pd.read_csv(os.path.join(dataframes_path, 'edges.csv'))

    # Tracks output path and others
    tracks_output_path = os.path.join(output_path, 'Tracks-Output')
    partial_edges_path = os.path.join(tracks_output_path, 'Partial-Edges')

    # Create the information dataframe
    info_groups = tracks_info_df[['track_id','difficulty','year','month','season','weekday','weather_condition','total_distance','total_time','average_pace','elevation_gain']]

    # Apply the groups
    info_groups['distance_group'] = info_groups['total_distance'].apply(apply_distance_group)    # 1 to 7
    info_groups['time_group'] = info_groups['total_time'].apply(apply_time_group)                # 1 to 7
    info_groups['pace_group'] = info_groups['average_pace'].apply(apply_pace_group)              # 1 to 4
    info_groups['elevation_gain_group'] = info_groups['elevation_gain'].apply(apply_elevation_group)    # 1 to 5

    # Create the edges dataframes directory
    edges_dir_path = os.path.join(dataframes_path, 'Edges-Dataframes')
    os.makedirs(edges_dir_path, exist_ok=True)

    # Full edges dataframe
    dataframe_path = os.path.join(edges_dir_path, 'all_edges.csv')
    partial_edges_df = create_partial_edges_df(info_groups['track_id'].unique().tolist(), edges_df, partial_edges_path)   
    partial_edges_df.to_csv(dataframe_path, index=False)

    # For each difficulty level
    for difficulty in info_groups['difficulty'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'difficulty_{difficulty.lower().replace(" ", "_")}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['difficulty'] == difficulty]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each year
    for year in info_groups['year'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'year_{year}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['year'] == year]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each month
    for month in info_groups['month'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'month_{month.lower().replace(" ", "_")}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['month'] == month]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each season
    for season in info_groups['season'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'season_{season.lower().replace(" ", "_")}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['season'] == season]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each weather condition
    for weather in info_groups['weather_condition'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'weather_{weather.lower().replace(" ", "_")}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['weather_condition'] == weather]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each distance group
    for distance in info_groups['distance_group'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'distance_{distance}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['distance_group'] == distance]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each time group
    for time in info_groups['time_group'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'time_{time}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['time_group'] == time]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each pace group
    for pace in info_groups['pace_group'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'pace_{pace}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['pace_group'] == pace]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

    # For each elevation gain group
    for elevation in info_groups['elevation_gain_group'].unique().tolist():

        # Get the path
        dataframe_path = os.path.join(edges_dir_path, f'elevation_{elevation}.csv')

        # Only if the dataframe does not exist
        if not os.path.exists(dataframe_path):

            # Obtain the partial df
            partial_df = info_groups[info_groups['elevation_gain_group'] == elevation]
            list_tracks = partial_df['track_id'].unique().tolist()

            # Apply the function
            partial_edges_df = create_partial_edges_df(list_tracks, edges_df, partial_edges_path)    

            # Save the dataframe
            partial_edges_df.to_csv(dataframe_path, index=False)

