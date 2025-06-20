import pandas as pd
from pandas.errors import SettingWithCopyWarning
import os
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)

# Dictionaries with the colors of the groups
pace_color_dict = {'Less than 15 min/km':'#ae017e', 'From 15 to 30 min/km':'#f768a1', 'From 30 to 45 min/km':'#fbb4b9', 'More than 45 min/km':'#feebe2'}
tracks_color_dict = {'Less than 25 tracks':'#ffffb2', 'From 25 to 50 tracks':'#fecc5c', 'From 50 to 75 tracks':'#fd8d3c', 'More than 75 tracks':'#e31a1c'}

# Formats the pace
def format_pace(pace_min_per_km):

    # Obtain the minutes and the seconds
    minutes = int(pace_min_per_km)
    seconds = int(round((pace_min_per_km - minutes) * 60))

    # Concatenate it
    if seconds == 60:
        minutes += 1
        seconds = 0
    
    return f"{minutes}:{seconds:02d} min/km"

# Group the average pace column in four groups
def average_pace_group(average_pace):

    # Four groups, depend on the value (in min/km)
    if average_pace < 15:
        return 'Less than 15 min/km'
    elif (average_pace >= 15) & (average_pace < 30):
        return 'From 15 to 30 min/km'
    elif (average_pace >= 30) & (average_pace < 45):
        return 'From 30 to 45 min/km'
    else:
        return 'More than 45 min/km'

# Group the total tracks column in four groups
def total_tracks_group(total_tracks):

    # Four groups, depend on the value (in min/km)
    if total_tracks < 25:
        return 'Less than 25 tracks'
    elif (total_tracks >= 25) & (total_tracks < 50):
        return 'From 25 to 50 tracks'
    elif (total_tracks >= 50) & (total_tracks < 75):
        return 'From 50 to 75 tracks'
    else:
        return 'More than 75 tracks'

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
    partial_edges_df['avg_pace'] = round(partial_edges_df['list_avg_pace'].apply(lambda paces: np.mean(paces) if paces else None), 2)

    # Normalize the average pace column
    # Calculate the IQR
    Q1 = partial_edges_df['avg_pace'].quantile(0.35)
    Q3 = partial_edges_df['avg_pace'].quantile(0.65)
    IQR = Q3 - Q1

    # Define the bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Calculate the mean without the outliers to put it into the outpliers
    mean_without_outliers = partial_edges_df.loc[(partial_edges_df['avg_pace'] >= lower_bound) & (partial_edges_df['avg_pace'] <= upper_bound), 'avg_pace'].mean()

    # Apply the values
    partial_edges_df['avg_pace'] = round(partial_edges_df['avg_pace'].apply(lambda x: mean_without_outliers if (x < lower_bound or x > upper_bound) else x), 2)

    # Apply the pace group, and the color
    partial_edges_df['pace_group'] = partial_edges_df['avg_pace'].apply(average_pace_group)
    partial_edges_df['pace_color'] = partial_edges_df['pace_group'].map(pace_color_dict)

    # Apply the total tracks group, and the color
    partial_edges_df['total_tracks_group'] = partial_edges_df['total_tracks'].apply(total_tracks_group)
    partial_edges_df['total_tracks_color'] = partial_edges_df['total_tracks_group'].map(tracks_color_dict)

    # Create empty columns for tooltip and popup
    partial_edges_df['map_tooltip'] = None
    partial_edges_df['map_popup'] = None

    for index, row in partial_edges_df.iterrows():

        # Create the tooltip and add it into the dataframe
        tooltip_html = f'Edge <b>{row['id']}</b>'
        partial_edges_df.at[index, 'map_tooltip'] = tooltip_html

        # Form the average pace
        formatted_pace = format_pace(row['avg_pace'])

        # Create the popup
        popup_html = f'''<div style="font-size: 10px;">
                        <b>Edge {row['id']}</b><br>
                        <ul style="padding-left: 16px; margin: 4px 0;">
                            <li><b>Total registered tracks</b>: {row['total_tracks']}</li>
                            <li><b>Average pace</b>: {formatted_pace}</li>
                        </ul></div>'''

        # Add the popup to the dataframe
        partial_edges_df.at[index, 'map_popup'] = popup_html

    # Reorder the dataframe
    partial_edges_df = partial_edges_df[['id','avg_pace','pace_group','pace_color','total_tracks','total_tracks_group','total_tracks_color','list_tracks','map_tooltip','map_popup','geometry']]

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
    info_groups = tracks_info_df[['track_id','difficulty','year','weather_condition']]

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