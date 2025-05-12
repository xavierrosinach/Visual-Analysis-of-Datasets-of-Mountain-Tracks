from streamlit_echarts import st_echarts
import os
import json

def show_vis(vis_path):

    with open(vis_path, "r", encoding="utf-8") as file:
        options = json.load(file)

    st_echarts(options=options)

visualizations_path = '../Visualizations'

show_vis(os.path.join(visualizations_path, 'prova.json'))
