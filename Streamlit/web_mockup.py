import streamlit as st
import home_page
import canigo_home
import matagalls_home
import vallferrera_home

# Page configuration
st.set_page_config(page_title="Visual Analysis of Datasets of Mountain Tracks",
                   page_icon="⛰️",
                   layout="wide")

# Pages dict
pages = {"🏠 Home": home_page,
         "🏔️ El Canigó": canigo_home,
         "🏔️ El Matagalls": matagalls_home,
         "🏔️ La Vall Ferrera": vallferrera_home}

# Sidebar selection
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page", list(pages.keys()))

# Show the page
pages[page].app()
