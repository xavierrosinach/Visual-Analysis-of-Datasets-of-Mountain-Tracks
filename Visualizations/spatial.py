import pandas as pd
from pandas.errors import SettingWithCopyWarning
import folium
from shapely import wkt
import numpy as np
import ast
from folium.plugins import GroupedLayerControl
from branca.element import Template, MacroElement
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)

# Dictionaries with the colors of the groups
pace_color_dict = {'Less than 15 min/km':'#ae017e', 'From 15 to 30 min/km':'#f768a1', 'From 30 to 45 min/km':'#fbb4b9', 'More than 45 min/km':'#feebe2'}
uphill_color_dict = {'Less than 7.5%':'#f1eef6', 'From 7.5% to 15%':'#bdc9e1', 'From 15% to 22.5%':'#74a9cf', 'More than 22.5%':'#0570b0'}
tracks_color_dict = {'Less than 25 tracks':'#ffffb2', 'From 25 to 50 tracks':'#fecc5c', 'From 50 to 75 tracks':'#fd8d3c', 'More than 75 tracks':'#e31a1c'}
comparison_color_dict = {'Fastest':'#3ca951', 'Slowest':'#ff725c'}

# Dictionary with the center coordinates
center_coords_dict = {"canigo": (2.5, 42.5), "matagalls": (2.4, 41.825), "vallferrera": (1.35, 42.6), "exemple": (2.4, 41.825)}

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

# Given the total minutes, divide it into hours, minutes and seconds
def format_time(total_minutes):

    # Calculate hours, minutes and seconds
    total_seconds = int(total_minutes * 60)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Put it in parts, and join it
    parts = []
    if hours > 0:
        parts.append(f"{hours} h")
    if minutes > 0:
        parts.append(f"{minutes} min")
    if hours == 0 and minutes == 0:     # Only show the seconds if the time is less than a minute (not frequent)
        parts.append(f"{seconds} sec")

    return ', '.join(parts)

# Combine the track and the full edges dataframe to obtain other metrics
def combine_edges_dfs(all_edges_df, track_edges_df):

    # Select some columns and rename it
    all_edges_df_cut = all_edges_df[['id','avg_pace','pace_group','pace_color','total_tracks','total_tracks_group','total_tracks_color']]
    all_edges_df_cut = all_edges_df_cut.rename(columns={'id':'edge_id','avg_pace':'all_tracks_avg_pace','pace_group':'all_tracks_pace_group','pace_color':'all_tracks_avg_color'})

    # Merge the dataframes
    merged_df = track_edges_df.merge(all_edges_df_cut, on='edge_id')

    # Compare the column with the mean
    merged_df['fast_slow_mean'] = np.where(merged_df['avg_pace'] <= merged_df['all_tracks_avg_pace'], 'Fastest', 'Slowest')
    merged_df['fast_slow_color'] = merged_df['fast_slow_mean'].map(comparison_color_dict)

    # Create empty columns for tooltip and popup html formatted texts
    merged_df['map_tooltip'] = None
    merged_df['map_popup'] = None

    for index, row in merged_df.iterrows():

        # Create the tooltip
        tooltip_html = f'Edge <b>{row['edge_id']}</b>'
        merged_df['map_tooltip'].iloc[index] = tooltip_html
        
        # Format the time and the pace column
        pace_formatted = format_pace(row['avg_pace'])
        all_tracks_pace_formatted = format_pace(row['all_tracks_avg_pace'])
        time_formatted = format_time(row['time'])

        # Create the popup
        popup_html = f'''<div style="font-size: 10px;">
                        <b>Edge {row['edge_id']}</b><br>
                        <ul style="padding-left: 16px; margin: 4px 0;">
                            <li><b>Distance</b>: {row['dist']:.2f} km</li>
                            <li><b>Time</b>: {time_formatted}</li>
                            <li><b>Elevation gain</b>: {row['elev_gain']:.2f} meters</li>
                            <li><b>Uphill percentage</b>: {row['uphill_perc']:.2f} %</li>
                            <li><b>Average pace</b>: {pace_formatted}</li>
                            <li><b>All tracks average pace</b>: {all_tracks_pace_formatted}</li>
                            <li><b>Fastest or slowest than the mean pace</b>: {row['fast_slow_mean']}</li>
                            <li><b>Popularity of the edge</b>: {row['total_tracks']} tracks</li>
                        </ul></div>'''
        
        # Add the popup to the dataframe
        merged_df['map_popup'].iloc[index] = popup_html

    return merged_df

# Given each dictionary, create the legend (able to be clicked and show it)
def create_html_legend(dict, title, position):

    # Add the entries to a list
    legend_entries = []
    for value in dict:
        html_def = f"""<div style="margin-bottom: 4px;">
            <i style="background:{dict[value]};width:15px;height:15px;display:inline-block;margin-right:6px;"></i>{value}
        </div>"""
        legend_entries.append(html_def)

    # HTML legend
    legend_html = f"""{{% macro html(this, kwargs) %}}
        <div style="position: fixed; 
                    bottom: 40px; left: {position}px; width: 220px;
                    z-index:9999; font-size:10px;">

            <button onclick="var el = document.getElementById('legend-content-{title}');
                             el.style.display = el.style.display === 'none' ? 'block' : 'none';"
                    style="width: 100%; padding: 6px; font-size: 12px; cursor: pointer;
                           border: 2px solid grey; border-radius: 5px;
                           background: white; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
                {title}
            </button>

            <div id="legend-content-{title}" style="display: none;
                         background: white; padding: 10px;
                         border:2px solid grey; border-radius: 5px;
                         box-shadow: 2px 2px 6px rgba(0,0,0,0.3); margin-top: 5px;">
                {''.join(legend_entries)}
            </div>
        </div>
    {{% endmacro %}}"""

    # Create the element
    legend = MacroElement()
    legend._template = Template(legend_html)
    return legend

# Creates the full track tooltip and popup
def create_track_tooltip_popup(track_info):

    # Create the tooltip
    tooltip_html = f'Track <b>{track_info['track_id'].iloc[0]}</b></b>'

    # Format the time and the pace column
    pace_formatted = format_pace(track_info['average_pace'].iloc[0])
    time_formatted = format_time(track_info['total_time'].iloc[0])

    # Create the popup
    popup_html = f'''<div style="font-size: 10px;">
                        <b>Track {track_info['track_id'].iloc[0]}</b><br>
                        <ul style="padding-left: 16px; margin: 4px 0;">
                            <li><b>Title</b>: {track_info['title'].iloc[0]}</li>
                            <li><b>Difficulty</b>: {track_info['difficulty'].iloc[0]}</li>
                            <li><b>Date</b>: {track_info['date'].iloc[0]}</li>
                            <li><b>Distance</b>: {track_info['total_distance'].iloc[0]} km</li>
                            <li><b>Time</b>: {time_formatted}</li>
                            <li><b>Average pace</b>: {pace_formatted}</li>
                            <li><b>Elevation gain</b>: {track_info['elevation_gain'].iloc[0]} meters</li>
                            <li><a href="{track_info['url'].iloc[0]}" target="_blank">Link to Wikiloc</a></li>
                        </ul></div>'''
    
    return tooltip_html, popup_html

# Create the points tooltips and popups
def create_points_tooltips_popups(track_df, max_elev_idx, min_elev_idx):

    # Tooltip and popup for the start point
    tooltip_start_point = 'Starting point'
    popup_start_point = f'''<div style="font-size: 10px;">
                            <b>Starting point</b><br>
                            <ul style="padding-left: 16px; margin: 4px 0;">
                                <li><b>Latitude</b>: {track_df['lat'].iloc[0]}</li>
                                <li><b>Longitude</b>: {track_df['lon'].iloc[0]}</li>
                                <li><b>Elevation</b>: {track_df['elev'].iloc[0]} meters</li>
                            </ul></div>'''
    
    # Tooltip and popup for the end point
    tooltip_end_point = 'Ending point'
    popup_end_point = f'''<div style="font-size: 10px;">
                            <b>Ending point</b><br>
                            <ul style="padding-left: 16px; margin: 4px 0;">
                                <li><b>Latitude</b>: {track_df['lat'].iloc[-1]}</li>
                                <li><b>Longitude</b>: {track_df['lon'].iloc[-1]}</li>
                                <li><b>Elevation</b>: {track_df['elev'].iloc[-1]} meters</li>
                            </ul></div>'''
    
    # Tooltip and popup for the highest point
    tooltip_highest_point = 'Highest point'
    popup_highest_point = f'''<div style="font-size: 10px;">
                            <b>Highest point</b><br>
                            <ul style="padding-left: 16px; margin: 4px 0;">
                                <li><b>Latitude</b>: {track_df['lat'].iloc[max_elev_idx]}</li>
                                <li><b>Longitude</b>: {track_df['lon'].iloc[max_elev_idx]}</li>
                                <li><b>Elevation</b>: {track_df['elev'].iloc[max_elev_idx]} meters</li>
                            </ul></div>'''
    
    # Tooltip and popup for the lowest point
    tooltip_lowest_point = 'Lowest point'
    popup_lowest_point = f'''<div style="font-size: 10px;">
                            <b>Lowest point</b><br>
                            <ul style="padding-left: 16px; margin: 4px 0;">
                                <li><b>Latitude</b>: {track_df['lat'].iloc[min_elev_idx]}</li>
                                <li><b>Longitude</b>: {track_df['lon'].iloc[min_elev_idx]}</li>
                                <li><b>Elevation</b>: {track_df['elev'].iloc[min_elev_idx]} meters</li>
                            </ul></div>'''

    return tooltip_start_point, popup_start_point, tooltip_end_point, popup_end_point, tooltip_highest_point, popup_highest_point, tooltip_lowest_point, popup_lowest_point

# Create the single track map
def create_track_map(track_id, tracks_info, all_edges_df, waypoints_df, track_df, track_km_df, track_pace_df, track_edges_df):

    # Read the information and waypoints
    track_info = tracks_info[tracks_info['track_id'] == track_id]
    waypoints_df = waypoints_df[waypoints_df['track_id'] == track_id]

    # Combine the edges dataframes
    track_edges_df = combine_edges_dfs(all_edges_df, track_edges_df)

    # Mean coordinates to center the map
    mean_coords = [track_df['lat'].mean(), track_df['lon'].mean()]

    # Generate the background map
    m = folium.Map(location=mean_coords, zoom_start=14, control_scale=True, tiles=None)

    # Different tiles to the map
    folium.TileLayer('OpenStreetMap', name='Open Street Map', show=True).add_to(m)
    folium.TileLayer('CartoDB positron', name='White Background', show=False).add_to(m)
    folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     name='Esri Satellite',
                     attr='Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
                     show=False).add_to(m)

    # Coordinates as a list
    full_track_coords = track_df[['lat', 'lon']].values.tolist()
    folium.PolyLine(locations=full_track_coords, color='black', weight=6).add_to(m)

    # Create the layers, and add them to the map
    full_track = folium.FeatureGroup(name="Full track", show=True)
    km_alternate = folium.FeatureGroup(name="Kilometer division - Alternate", show=False)
    km_pace = folium.FeatureGroup(name="Kilometer division - Average pace", show=False)
    km_uphill = folium.FeatureGroup(name="Kilometer division - Uphill %", show=False)
    pace_pace = folium.FeatureGroup(name="Pace zones division - Average pace", show=False)
    pace_uphill = folium.FeatureGroup(name="Pace zones division - Uphill %", show=False)
    edges_pace = folium.FeatureGroup(name="Edges division - Average pace", show=False)
    edges_pace_all = folium.FeatureGroup(name="Edges division - Average pace (all tracks)", show=False)
    edges_fast_slow = folium.FeatureGroup(name="Edges division - Pace comparison with all tracks", show=False)
    edges_uphill = folium.FeatureGroup(name="Edges division - Uphill %", show=False)
    edges_popul = folium.FeatureGroup(name="Edges division - Popularity", show=False)

    # Create the points
    start_point = folium.FeatureGroup(name="Start point", show=True)
    end_point = folium.FeatureGroup(name="End point", show=True)
    highest_point = folium.FeatureGroup(name="Highest point", show=False)
    lowest_point = folium.FeatureGroup(name="Lowest point", show=False)
    kms_division = folium.FeatureGroup(name="Kilometers division", show=False)

    # Create and add all FeatureGroups to the map
    layers = [full_track, km_alternate, km_pace, km_uphill, pace_pace, pace_uphill, edges_pace, edges_pace_all, edges_fast_slow, edges_uphill, edges_popul]
    points = [start_point, end_point, highest_point, lowest_point, kms_division]

    # Add each feature group to the map
    for layer in layers:
        m.add_child(layer)

    # Add each point to the map
    for point in points:
        m.add_child(point)

    # Add the full track polyline to the map, create the tooltip and the popup
    full_tooltip, full_popup = create_track_tooltip_popup(track_info)
    folium.PolyLine(locations=full_track_coords, tooltip=full_tooltip, popup=folium.Popup(full_popup, max_width=300), color='#efb118', weight=4).add_to(full_track)

    # Add the kilometer division three layers - and the km points
    for index, row in track_km_df.iterrows():

        # Convert to Shapely LineString
        line = wkt.loads(row['geometry'])
        coords = [[lat, lon] for lon, lat in line.coords]   # Define the coordinates

        # Obtain the tooltip and the popup
        tooltip = row['map_tooltip']
        popup1 = folium.Popup(row['map_popup'], max_width=300)     # Three popups because we can not use the same
        popup2 = folium.Popup(row['map_popup'], max_width=300)
        popup3 = folium.Popup(row['map_popup'], max_width=300)

        # Add the three layers
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup1, color=row['alternate_color'], weight=4).add_to(km_alternate)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup2, color=row['pace_color'], weight=4).add_to(km_pace)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup3, color=row['uphill_perc_color'], weight=4).add_to(km_uphill)

        # Add the kilometers markers
        if index != 0:
            # Add the marker with text inside
            folium.Marker(location=coords[0], tooltip=f'Kilometer <b>{row['km']}</b>', popup=folium.Popup(f'<b>Kilometer {row['km']}</b>', max_width=300),
                        icon=folium.DivIcon(html=f"""<div style="background-color: yellow; border: 2px solid black; border-radius: 50%; width: 20px; height: 20px;
                                                                                                                text-align: center; font-size: 10pt; font-weight: bold; line-height: 20px;">{row['km']}</div>""")).add_to(kms_division)

    # Add the pace zones two layers
    for index, row in track_pace_df.iterrows():

        # Convert to Shapely LineString
        line = wkt.loads(row['geometry'])
        coords = [[lat, lon] for lon, lat in line.coords]   # Define the coordinates

        # Obtain the tooltip and the popup
        tooltip = row['map_tooltip']
        popup1 = folium.Popup(row['map_popup'], max_width=300)     # Three popups because we can not use the same
        popup2 = folium.Popup(row['map_popup'], max_width=300)

        # Add the three layers
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup1, color=row['pace_color'], weight=4).add_to(pace_pace)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup2, color=row['uphill_perc_color'], weight=4).add_to(pace_uphill)

    # Add the edges division five layers
    for index, row in track_edges_df.iterrows():

        # Convert to Shapely LineString
        line = wkt.loads(row['geometry'])
        coords = [[lat, lon] for lon, lat in line.coords]   # Define the coordinates

        # Obtain the tooltip and the popup
        tooltip = row['map_tooltip']
        popup1 = folium.Popup(row['map_popup'], max_width=300)     # Three popups because we can not use the same
        popup2 = folium.Popup(row['map_popup'], max_width=300)
        popup3 = folium.Popup(row['map_popup'], max_width=300)
        popup4 = folium.Popup(row['map_popup'], max_width=300)
        popup5 = folium.Popup(row['map_popup'], max_width=300)

        # Add the three layers
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup1, color=row['pace_color'], weight=4).add_to(edges_pace)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup2, color=row['all_tracks_avg_color'], weight=4).add_to(edges_pace_all)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup3, color=row['uphill_perc_color'], weight=4).add_to(edges_uphill)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup4, color=row['total_tracks_color'], weight=4).add_to(edges_popul)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup5, color=row['fast_slow_color'], weight=4).add_to(edges_fast_slow)

    # Obtain the maximum and minimum elevation points index
    max_elev_idx = int(track_df.loc[track_df['elev'].idxmax(), ['id']].iloc[0] - 1)
    min_elev_idx = int(track_df.loc[track_df['elev'].idxmin(), ['id']].iloc[0] - 1)

    # Create the folium tooltips and popups
    tooltip_start_point, popup_start_point, tooltip_end_point, popup_end_point, tooltip_highest_point, popup_highest_point, tooltip_lowest_point, popup_lowest_point = create_points_tooltips_popups(track_df, max_elev_idx, min_elev_idx)

    # Create the first and the last points
    folium.Marker(location=full_track_coords[0], tooltip=tooltip_start_point, popup=folium.Popup(popup_start_point, max_width=300), icon=folium.Icon(color='green', icon='play', prefix='fa')).add_to(start_point)     # Start point
    folium.Marker(location=full_track_coords[-1], tooltip=tooltip_end_point, popup=folium.Popup(popup_end_point, max_width=300), icon=folium.Icon(color='red', icon='stop', prefix='fa')).add_to(end_point)        # End point

    # Add the highest and the lowest points
    folium.Marker(location=full_track_coords[max_elev_idx], tooltip=tooltip_highest_point, popup=folium.Popup(popup_highest_point, max_width=300), icon=folium.Icon(color='blue', icon='up-long', prefix='fa')).add_to(highest_point)     # Highest point
    folium.Marker(location=full_track_coords[min_elev_idx], tooltip=tooltip_lowest_point, popup=folium.Popup(popup_lowest_point, max_width=300), icon=folium.Icon(color='blue', icon='down-long', prefix='fa')).add_to(lowest_point)     # Lowest point

    # Add markers for each waypoint if it has waypoints
    if len(waypoints_df) > 0:

        # Create the selection and add it to the map
        points_interest = folium.FeatureGroup(name="Points of interest", show=False)
        points = [start_point, end_point, highest_point, lowest_point, points_interest, kms_division]
        m.add_child(points_interest)

        # For each waypoint
        for index, row in waypoints_df.iterrows():
            folium.Marker(location=[row['lat'], row['lon']], tooltip=row['map_tooltip'], popup=folium.Popup(row['map_popup'], max_width=300), icon=folium.Icon(color='orange', icon=row['icon'], prefix='fa')).add_to(points_interest)

    # Create and add the legends
    pace_legend = create_html_legend(pace_color_dict, 'Average pace - legend', 30)
    uphill_legend = create_html_legend(uphill_color_dict, 'Uphill % - legend', 260)
    popularity_legend = create_html_legend(tracks_color_dict, 'Popularity - legend', 490)
    comparison_legend = create_html_legend(comparison_color_dict, 'Comparison with all tracks - legend', 720)
    m.add_child(pace_legend)
    m.add_child(uphill_legend)
    m.add_child(popularity_legend)
    m.add_child(comparison_legend)

    # Add the folium layer control
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    GroupedLayerControl(groups={'Track painting': layers}, collapsed=True).add_to(m)
    GroupedLayerControl(groups={'Add widgets': points}, exclusive_groups=False, collapsed=True).add_to(m)

    return m

# Given an edges dataframe, create the full map
def create_edges_map(edges_df, zone, tracks_info, waypoints_df):

    # Obtain the center coords 
    center_coords = center_coords_dict[zone]

    # Generate the background map
    m = folium.Map(location=[center_coords[1], center_coords[0]], zoom_start=12, control_scale=True, tiles=None)

    # Different tiles to the map
    folium.TileLayer('OpenStreetMap', name='Open Street Map', show=True).add_to(m)
    folium.TileLayer('CartoDB positron', name='White Background', show=False).add_to(m)
    folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                        name='Esri Satellite',
                        attr='Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
                        show=False).add_to(m)

    # Create the layers
    popularity = folium.FeatureGroup(name="Popularity", show=True)
    avg_pace = folium.FeatureGroup(name="Average pace", show=True)

    # Create the points
    starting_points = folium.FeatureGroup(name="Starting points", show=False)
    ending_point = folium.FeatureGroup(name="Ending points", show=False)
    waypoints = folium.FeatureGroup(name="Points of interest", show=False)

    # Create and add all FeatureGroups to the map
    layers = [popularity, avg_pace]
    points = [starting_points, ending_point, waypoints]

    # Add each feature group to the map
    for layer in layers:
        m.add_child(layer)

    # Add each point to the map
    for point in points:
        m.add_child(point)

    # Add the pace legend to legends
    popularity_legend = create_html_legend(tracks_color_dict, 'Popularity - legend', 30)
    pace_legend = create_html_legend(pace_color_dict, 'Average pace - legend', 260)
    m.add_child(pace_legend)
    m.add_child(popularity_legend)

    # For each edge, add the line
    for index, row in edges_df.iterrows():
        
        # Convert to Shapely LineString
        line = wkt.loads(row['geometry'])
        coords = [[lat, lon] for lon, lat in line.coords]   # Define the coordinates

        # Obtain the tooltip and the popup
        tooltip = row['map_tooltip']
        popup1 = folium.Popup(row['map_popup'], max_width=300)     # Three popups because we can not use the same
        popup2 = folium.Popup(row['map_popup'], max_width=300)

        # # Add a black line for the background
        folium.PolyLine(locations=coords, color='black', weight=6).add_to(popularity)
        folium.PolyLine(locations=coords, color='black', weight=6).add_to(avg_pace)

        # Add the three layers
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup1, color=row['total_tracks_color'], weight=4).add_to(popularity)
        folium.PolyLine(locations=coords, tooltip=tooltip, popup=popup2, color=row['pace_color'], weight=4).add_to(avg_pace)  

    # Add the starting and ending points
    for index, row in tracks_info.iterrows():

        # Get the first and the last coordinate as pairs
        start_coords = list(ast.literal_eval(row['first_coordinate']))
        end_coords = list(ast.literal_eval(row['last_coordinate']))

        # Create the toolip
        tooltip_html = f'Track <b>{row['track_id']}</b>'


        # Create the popup
        start_popup_html = f'''<div style="font-size: 10px;">
                        <b>Track {row['track_id']}</b><br>
                        <ul style="padding-left: 16px; margin: 4px 0;">
                            <li><b>Title</b>: {row['title']}</li>
                            <li><b>Longitude</b>: {start_coords[0]}</li>
                            <li><b>Latitude</b>: {start_coords[1]}</li>
                            <li><a href="{row['url']}" target="_blank">Link to Wikiloc</a></li>
                        </ul></div>'''
        end_popup_html = f'''<div style="font-size: 10px;">
                        <b>Track {row['track_id']}</b><br>
                        <ul style="padding-left: 16px; margin: 4px 0;">
                            <li><b>Title</b>: {row['title']}</li>
                            <li><b>Longitude</b>: {end_coords[0]}</li>
                            <li><b>Latitude</b>: {end_coords[1]}</li>
                            <li><a href="{row['url']}" target="_blank">Link to Wikiloc</a></li>
                        </ul></div>'''

        # Create green circles for the starting zone, and red circles for the ending
        folium.CircleMarker(location=start_coords, tooltip=tooltip, popup=folium.Popup(start_popup_html, max_width=300), radius=5, fill=True, fillOpacity=0.75, color='green').add_to(starting_points)  
        folium.CircleMarker(location=end_coords, tooltip=tooltip, popup=folium.Popup(end_popup_html, max_width=300), radius=5, fill=True, fillOpacity=0.75, color='red').add_to(ending_point)  

    # Add the waypoints
    for index, row in waypoints_df.iterrows():
        folium.CircleMarker(location=[row['lat'], row['lon']], tooltip=row['map_tooltip'], popup=folium.Popup(row['map_popup'], max_width=300), radius=5, fill=True, fillOpacity=0.75, color='orange').add_to(waypoints)  


    # Add the layer control
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    GroupedLayerControl(groups={'Edges painting': layers}, collapsed=True).add_to(m)
    GroupedLayerControl(groups={'Add widgets': points}, exclusive_groups=False, collapsed=True).add_to(m)

    return m