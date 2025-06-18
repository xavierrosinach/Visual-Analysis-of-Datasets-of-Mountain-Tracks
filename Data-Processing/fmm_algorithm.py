import pandas as pd
import os
import json
import geopandas as gpd
from geopy.distance import geodesic
from shapely.wkt import loads
from shapely.geometry import LineString
from fmm import Network,NetworkGraph,UBODTGenAlgorithm,UBODT,FastMapMatch, FastMapMatchConfig

# Define the bounds for each zone
bounds_dict = {"canigo": (2.2, 2.7, 42.4, 42.6), "matagalls": (2.3, 2.5, 41.8, 41.9), "vallferrera": (1.2, 1.7, 42.5, 42.8), "exemple": (2.3, 2.5, 41.8, 41.9)}

# Create needed datclearaframes
def create_dataframes(dataframes_path, osm_path):

    # Fast Map Matching configuration dataframe
    fmm_conf_path = os.path.join(dataframes_path, 'fmm_config.csv')
    if os.path.exists(fmm_conf_path):   # Check if it exists
        fmm_conf_df = pd.read_csv(fmm_conf_path)
    else:   # If it does not exist, we create if
        fmm_conf_df = pd.DataFrame(columns=['track_id','k','radius','gps_error'])
        fmm_conf_df.to_csv(fmm_conf_path, index=False)   # Save the dataframe as csv

    # Discarded tracks dataframe
    disc_path = os.path.join(dataframes_path, 'discarded.csv')
    if os.path.exists(disc_path):   # Check if it exists
        disc_df = pd.read_csv(disc_path)
    else:   # If it does not exist, we create if
        disc_df = pd.DataFrame(columns=['track_id','error_type'])
        disc_df.to_csv(disc_path, index=False)   # Save the dataframe as csv    

    return fmm_conf_df, fmm_conf_path, disc_df, disc_path

# Checks if the file is valid depending on the coordinates
def check_coordinates(track_id, coords_df, bounds, disc_df, disc_path):

    # Check if all the coordinates are inside the bounds
    inside_bounds = ((coords_df["Longitude"] >= bounds[0]).all() & (coords_df["Longitude"] <= bounds[1]).all() &
                     (coords_df["Latitude"] >= bounds[2]).all() & (coords_df["Latitude"] <= bounds[3]).all())
    
    if not inside_bounds:   # If the track is not in the defined bounds, error type 2
        disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[2]})], ignore_index=True)
        disc_df.to_csv(disc_path, index=False)
        return disc_df, False
    
    # Check if the coordinates dataframe has more than 100 coordinates
    if len(coords_df) < 100:
        disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[3]})], ignore_index=True)
        disc_df.to_csv(disc_path, index=False)
        return disc_df, False
    
    total_distance = 0.0    # Initialize a value for the total distance

    # Check the distance between two consecutive coordinates is lower than 300 meters
    for i in range(len(coords_df) - 1):  # Stop at the second last row 
        lon1, lat1 = coords_df.loc[i, 'Longitude'], coords_df.loc[i, 'Latitude']
        lon2, lat2 = coords_df.loc[i + 1, 'Longitude'], coords_df.loc[i + 1, 'Latitude']
        
        part_distance = geodesic((lat1, lon1), (lat2, lon2)).meters          # Compute distance (in meters) using geopy
        total_distance += part_distance              # Sum the distance at the total distance

        if part_distance > 300:
            disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[4]})], ignore_index=True)
            disc_df.to_csv(disc_path, index=False)
            return disc_df, False


    # Check if the total distance is greater than 1000 meters
    if total_distance < 1000:
        disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[5]})], ignore_index=True)
        disc_df.to_csv(disc_path, index=False)
        return disc_df, False
    
    # Return the discarded dataframe and true if we can proceed it
    return disc_df, True

# Applies the FMM algorithm to find a matching track
def matching_track(model, coords_df):

    # Get the track wkt
    line = LineString(zip(coords_df["Longitude"], coords_df["Latitude"]))
    track_wkt = line.wkt

    k_candidates = [2,3,4]      # Define three candidates for k

    # Try for the three candidates
    for k in k_candidates:
        try:
            config = FastMapMatchConfig(k, 0.001, 0.001)   
            result = model.match_wkt(track_wkt, config)

            if result.pgeom.export_wkt().strip() != "LINESTRING()":     # If a result is found, return it
                return True, result, k, 0.001, 0.001

        except:
            return False, None, 0, 0, 0
        
    return False, None, 0, 0, 0

# Saves the FMM result to a dataframe
def save_fmm_result(fmm_result, track_id, fmm_out_path):

    # Obtain the output path
    output_path = os.path.join(fmm_out_path, str(track_id)+'.csv')

    # Get the list of cleaned coordinates
    new_track = fmm_result.pgeom.export_wkt()   # Export the fmm output
    line = loads(new_track)     # Convert to shapely LineString object
    coords = list(line.coords)      # Extract coordinates

    df = pd.DataFrame(columns=["lon", "lat"])   # Create empty dataframe
    df["lon"], df["lat"] = zip(*coords)     # Insert the coordinates

    # Obtain the information of the candidates
    candidates = []
    for c in fmm_result.candidates:
        candidates.append((c.source,c.target))
    track_edges = pd.DataFrame(candidates, columns=["u","v"])

    # Concatenate dataframes
    df = pd.concat([df.reset_index(drop=True), track_edges.reset_index(drop=True)], axis=1)
    df[['u', 'v']] = df.apply(lambda row: sorted([row['u'], row['v']]), axis=1, result_type='expand')   # Apply order

    # Save the dataframe
    df.to_csv(output_path, index=False)

# Main FMM function
def main_fmm(data_path, zone):

    # Obtain all the paths
    zone_path = os.path.join(data_path, zone)
    input_path = os.path.join(zone_path, 'Input-Data')
    osm_path = os.path.join(zone_path, 'OSM-Data')
    output_path = os.path.join(zone_path, 'Output-Data')
    dataframes_path = os.path.join(output_path, 'Data-Frames')
    fmm_out_path = os.path.join(output_path, 'FMM-Output')

    # Create or read needed dataframes to store information
    fmm_conf_df, fmm_conf_path, disc_df, disc_path = create_dataframes(dataframes_path, osm_path)

    # Get a list with the tracks ids already processed
    processed_tracks = list(set(disc_df['track_id'].unique().tolist() + fmm_conf_df['track_id'].unique().tolist()))

    # Obtain the FastMapMatching model of the zone with the network, the graph, and the udobt file
    network = Network(os.path.join(osm_path, 'edges.shp'), "fid", "u", "v")     # Network of the zone with FMM
    graph = NetworkGraph(network)   # Network graph of the zone with FMM
    ubodt = UBODT.read_ubodt_csv(os.path.join(osm_path, 'udobt.txt'))    # Read the UDOBT file
    model = FastMapMatch(network,graph,ubodt)   # Creation of the model using FMM

    # For each track, proceed with the fast map matching
    for track in os.listdir(input_path):
        track_id = int(track.split('.')[0])           # Obtain the track id
        if track_id not in processed_tracks:          # Only process the track if it is not already done

            # Print information
            print(f'    Processing track {track_id}.', end='\r', flush=True)

            track_path = os.path.join(input_path, track)

            # Load JSON data from the file
            with open(track_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Obtain the coordinates dataframe and the activity type
            activity_type = data.get("activity", {}).get("name")
            coords_df = pd.DataFrame(data["coordinates"], columns=["Longitude", "Latitude", "Elevation", "Timestamp"])

            # Error type 1 if the track is not 'Senderisme'
            if activity_type != 'Senderisme':
                disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[1]})], ignore_index=True)
                disc_df.to_csv(disc_path, index=False)

            else:
                disc_df, valid_file = check_coordinates(track_id, coords_df, bounds_dict[zone], disc_df, disc_path)

            if valid_file:
                valid_file, fmm_result, k, r, e = matching_track(model, coords_df)      # Apply the fast map matching algorithm

                if valid_file:

                    # Save the fmm configuration information
                    fmm_conf_df = pd.concat([fmm_conf_df, pd.DataFrame({'track_id':[track_id], 'k':[k], 'radius':[r], 'gps_error':[e]})], ignore_index=True)
                    fmm_conf_df.to_csv(fmm_conf_path, index=False)

                    # Save the result information into a dataframe in the FMM-Output directory
                    save_fmm_result(fmm_result, track_id, fmm_out_path)
                    
                else:
                    disc_df = pd.concat([disc_df, pd.DataFrame({'track_id':[track_id], 'error_type':[6]})], ignore_index=True)
                    disc_df.to_csv(disc_path, index=False)

            else:
                continue    # The file has been discarded before in check_coordinates()

