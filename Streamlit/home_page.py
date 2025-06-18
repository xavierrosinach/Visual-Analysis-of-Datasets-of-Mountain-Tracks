import streamlit as st

streamlit_data_path = '../../Data/Streamlit-Data'

def app():
    st.title("Visual Analysis of Datasets of Mountain Tracks")
    st.subheader("by: Xavier Rosinach Capell")

    st.markdown('---')

    # Write introduction
    with open(f'{streamlit_data_path}/Text/General/principal_page.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        st.write(content)
    
    st.markdown('---')