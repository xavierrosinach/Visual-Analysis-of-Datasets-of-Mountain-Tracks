import pandas as pd
import os
import json

# Function to process a waypoints dataframe if it exists
def process_partial_waypoints_df(data, track_id):
    
    # Read the info as pandas dataframe
    df_waypoints = pd.DataFrame(data['waypoints'])

    # Select the first url of the photos of each point
    df_waypoints['photo_url'] = df_waypoints['photos'].apply(lambda x: x[0]['url'] if x and isinstance(x, list) else None)

    # Add a column with the track id
    df_waypoints['track_id'] = track_id

    # Select some columns
    df_waypoints = df_waypoints[['track_id','id','lat','lon','elevation','name','pictogramName','photo_url']]

    # Rename columns
    df_waypoints = df_waypoints.rename(columns={'id':'poi_id', 'pictogramName':'type', 'photo_url':'photo'})
    
    return df_waypoints

# Main function to obtain the waypoints dataframe
def obtain_waypoints_df(data_path, zone):

    final_path = os.path.join(data_path,zone,'Output-Data','Data-Frames','waypoints.csv')

    if os.path.exists(final_path):
        return

    # Obtain the dataframe with the tracks information
    tracks_info = pd.read_csv(os.path.join(data_path,zone,'Output-Data','Data-Frames','tracks_info.csv'))

    # Obtain a list with the processed tracks
    processed_tracks = tracks_info['track_id'].unique().tolist()

    # Path with the initial JSON files
    input_json_files = os.path.join(data_path,zone,'Input-Data')

    # Create a list with all the dataframes to concatenate it in a future
    all_waypoints = []

    # For each processed track, read the JSON file
    for track in processed_tracks:
        
        # Obtain the json path, and read it
        json_track = os.path.join(input_json_files, str(track)+'.json')
        with open(json_track, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Check if the data of the waypoints is empty or not
        if not data['waypoints']:
            continue
        else:
            df = process_partial_waypoints_df(data, track)
            all_waypoints.append(df)  

    # Get the full dataframe
    waypoints_df = pd.concat(all_waypoints, ignore_index=True)

    # Dictionary with normalized types
    translation_dict={"Cascada":"Point of interest","Collada":"Hill","Llac":"Lake","Castell":"Monument","Monument":"Monument","Pont":"Monument","Cim":"Mountain top","Aparcament":"Parking",
                    "Foto":"Photo","Panoràmica":"Photo","Platja":"Point of interest","Aigües termals":"Point of interest","Ancoratge":"Point of interest","Cova":"Point of interest",
                    "Cul de sac":"Point of interest","Fi de paviment":"Point of interest","Geocache":"Point of interest","Intersecció":"Point of interest","Jaciment arqueològic":"Point of interest",
                    "Mina":"Point of interest","Museu":"Point of interest","Patrimoni de la Humanitat":"Point of interest","Picnic":"Point of interest","Porta":"Point of interest",
                    "Punt d'informació":"Point of interest","Punt d'interès":"Point of interest","Punt d'observació d'aus":"Point of interest","Ruïnes":"Point of interest",
                    "Sense especificar":"Point of interest","Túnel":"Point of interest","Avituallament":"Refuge","Càmping":"Refuge","Pernoctació":"Refuge","Refugi de muntanya":"Refuge",
                    "Refugi lliure":"Refuge","Lloc religiós":"Religious point","Risc":"Risk","Riu":"River","Font":"Water source","Arbre":"Wildlife","Fauna":"Wildlife","Flora":"Wildlife","Parc":"Wildlife"}

    # Map with the dictionary to obtain a general type
    waypoints_df['general_type'] = waypoints_df['type'].map(translation_dict).fillna('Point of interest')

    # Dictionary with the folium icons
    icons_dictionary = {'Refuge':'tent','Monument':'landmark','Point of interest':'eye','Lake':'water','Photo':'camera','Mountain top':'mountain','Hill':'mound',
                        'Water source':'faucet-drip','Wildlife':'paw','River':'bridge-water','Parking':'square-parking','Risk':'triangle-exclamation','Religious point':'church'}

    # Apply the mapping
    waypoints_df['icon'] = waypoints_df['general_type'].map(icons_dictionary)

    # Select some columns
    waypoints_df = waypoints_df[['track_id','poi_id','lat','lon','elevation','name','general_type','icon','photo']]
    waypoints_df = waypoints_df.rename(columns={'general_type':'type'})

    # Create empty columns for tooltip and popup
    waypoints_df['map_tooltip'] = None
    waypoints_df['map_popup'] = None

    for index, row in waypoints_df.iterrows():

        # Create the tooltip and add it into the dataframe
        tooltip_html = f'Point of interest <b>{row['poi_id']}</b>'
        waypoints_df['map_tooltip'].iloc[index] = tooltip_html

        # Check if it has photos, and insert the link if it has
        if pd.isna(row['photo']):
            # Create the popup
            popup_html = f'''<div style="font-size: 10px;">
                            <b>Point of interest {row['poi_id']}</b><br>
                            <ul style="padding-left: 16px; margin: 4px 0;">
                                <li><b>Longitude</b>: {row['lat']}</li>
                                <li><b>Latitude</b>: {row['lon']}</li>
                                <li><b>Elevation</b>: {row['elevation']:.2f} meters</li>
                                <li><b>Type</b>: {row['type']}</li>
                            </ul></div>'''
        else:
            # Create the popup
            popup_html = f'''<div style="font-size: 10px;">
                            <b>Point of interest {row['poi_id']}</b><br>
                            <ul style="padding-left: 16px; margin: 4px 0;">
                                <li><b>Longitude</b>: {row['lat']}</li>
                                <li><b>Latitude</b>: {row['lon']}</li>
                                <li><b>Elevation</b>: {row['elevation']:.2f} meters</li>
                                <li><b>Type</b>: {row['type']}</li>
                                <li><a href="{row['photo']}" target="_blank">Photo</a></li>
                            </ul></div>'''

        # Add the popup to the dataframe
        waypoints_df['map_popup'].iloc[index] = popup_html

    # Save the waypoints dataframe
    waypoints_df.to_csv(final_path, index=False)