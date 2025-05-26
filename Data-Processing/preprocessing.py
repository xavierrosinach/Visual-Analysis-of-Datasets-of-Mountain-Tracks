from fmm import Network,NetworkGraph,UBODTGenAlgorithm
import os
import osmnx as ox
from shapely.geometry import Polygon
import shutil
import zipfile

bounds_dict = {"canigo": (2.2, 2.7, 42.4, 42.6), "matagalls": (2.3, 2.5, 41.8, 41.9), "vallferrera": (1.2, 1.7, 42.5, 42.8), "exemple": (2.3, 2.5, 41.8, 41.9)}

# Unzip the zipped file, and drop all JSON files into the input directory
def extract_zip_file(data_path, zip_file_path, input_path):

    # Check if the input path exists to avoid execution
    if os.path.exists(input_path):
        return
    
    # Create a provisional directory to put all the files, at the end of the function, we will erase it
    provisional_path = os.path.join(data_path,'Provisional-Zip-Data')
    os.makedirs(provisional_path, exist_ok=True)

    # Extract the zip file to the provisional path
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        zip_file.extractall(provisional_path)

    # Create the input path
    os.makedirs(input_path, exist_ok=True)

    # For each directory of the provisional path, we check the JSON files
    for root, _, files in os.walk(provisional_path):
        for file in files:
            if file.endswith('.json'):
                shutil.copy2(os.path.join(root, file), os.path.join(input_path, file))  # Move the file from the root to the input directory

    # Remove the provisional path
    shutil.rmtree(provisional_path)

# Fills the OSM-Data directory with the needed data of OSM
def generate_osm_network(osm_path, zone, bound):

    # Check if the OSM-Data path is already filled
    if os.path.exists(osm_path):
        return
    
    # Create the directory
    os.makedirs(osm_path, exist_ok=True)

    # Create a network and the graph with OSMNX
    x1,x2,y1,y2 = bounds_dict.get(zone)      # Depending on the zone, select the bounds
    boundary_polygon = Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])   # Create the bounds polygon
    G = ox.graph_from_polygon(boundary_polygon, network_type='all')     # Create the graph (all type of paths)

    # Create the paths
    filepath_nodes = os.path.join(osm_path, "nodes.shp")    # Nodes shapefile
    filepath_edges = os.path.join(osm_path, "edges.shp")    # Edges shapefile

    # Convert undirected graph to GDFs and stringify non-numeric columns
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
    gdf_nodes = ox.io._stringify_nonnumeric_cols(gdf_nodes)
    gdf_edges = ox.io._stringify_nonnumeric_cols(gdf_edges)
    gdf_edges["fid"] = gdf_edges.index      # Create an index for each edge

    # Save the nodes and the edges as separate ESRI shapefiles
    gdf_nodes.to_file(filepath_nodes, encoding="utf-8")
    gdf_edges.to_file(filepath_edges, encoding="utf-8")

    # Create the UDOBT file, necessary for the FMM algorithm
    network = Network(filepath_edges, "fid", "u", "v")     # Network of the zone with FMM
    graph = NetworkGraph(network)   # Network graph of the zone with FMM

    # Create or read the UDOBT file
    udobt_path = os.path.join(osm_path, 'udobt.txt')
    ubodt_gen = UBODTGenAlgorithm(network,graph)
    ubodt_gen.generate_ubodt(udobt_path, 4, binary=False, use_omp=True)

# Creates all the directories
def main_preprocessing(data_path, zone):

    # Check if the zip file exists
    zip_file_path = os.path.join(data_path, 'Zip-Files', f'{zone}.zip')
    if not os.path.exists(zip_file_path):
        print(f'The zip file of the zone {zone} is not in directory Zip-Files.')
        return

    # Define the zone path and create it
    zone_path = os.path.join(data_path, zone)
    os.makedirs(zone_path, exist_ok=True)

    # Input data path
    input_path = os.path.join(zone_path, 'Input-Data')
    extract_zip_file(data_path, zip_file_path, input_path)

    # OSM data path
    osm_path = os.path.join(zone_path, 'OSM-Data')
    generate_osm_network(osm_path, zone, bounds_dict[zone])

    # Output data path
    output_path = os.path.join(zone_path, 'Output-Data')
    os.makedirs(output_path, exist_ok=True)

    # Data frames path
    dataframes_path = os.path.join(output_path, 'Data-Frames')
    os.makedirs(dataframes_path, exist_ok=True)

    # FMM output path
    fmm_out_path = os.path.join(output_path, 'FMM-Output')
    os.makedirs(fmm_out_path, exist_ok=True)
