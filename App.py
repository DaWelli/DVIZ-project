import pandas as pd
import streamlit as st

# -- Page config --
st.set_page_config(page_title='DVIZ Project: World in data',
                   page_icon=':earth_africa:',
                   layout='wide')


# -- Navbar --
def navbar():
    with st.sidebar:
        st.page_link('App.py', label='Home', icon='🏠')
        st.page_link('pages/Suicide.py', label='Suicide Data', icon='🌍')
        st.page_link('pages/About.py', label='About / Code', icon='❓')


navbar()

# -- Title --
st.title(':earth_africa: DVIZ Project - World in data')

st.write('Welcome to my DVIZ Project - World in Data. With this project, I aim to explore our world, specifically '
         'focusing on the population of each country, GDP, GNI, and their correlation with suicide, along with some '
         'tidbits here and there.')

st.image('https://cdn.pixabay.com/photo/2018/03/20/18/23/cartography-3244166_1280.png', use_column_width=True)

# -- Here I remove the Streamlit header and footer --
st.markdown(
    """
    <style>
        footer {display: none}
        [data-testid="stHeader"] {display: None}
    </style>
    """, unsafe_allow_html=True
)

# -- Loading CSS --
with open('style/styles.css') as f:
    css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


# -- Cache data --
@st.cache_data
def load_data(data):
    data = pd.read_csv(data)
    return data
