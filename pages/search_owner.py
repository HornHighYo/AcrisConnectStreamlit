# -*- coding: utf-8 -*-
"""
ACRIS_APP.PY

"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="ChatNYC")
st.title("SEARCH by Owner")
st.sidebar.title("SEARCH by Owner")

# Create form with user inputs
boroughs=['MN','BX','BK','QN','SI']
with st.sidebar:
    with st.form("address_form"):        
        selected_borough = st.selectbox('Select Borough', boroughs, index=boroughs.index('MN'))

#data
@st.cache_data
def load_data():
    file_path="data/pluto_testAug29.xlsx"
    df=pd.read_excel(file_path)
    return df

df = load_data()


# Create list of addresses for autocomplete
owners = df['ownername'].dropna().unique().tolist()

# Specify the columns to display in the filtered dataframe
columns_to_display = ['borough', 'block', 'lot', 'address', 'zipcode','zonedist1', 'bldgclass', 'landuse',
                      'ownertype', 'ownername', 'numfloors', 'unitsres', 'unitstotal', 'lotfront', 'lotdepth',
                      'bldgfront', 'bldgdepth',  'assessland', 'assesstot', 'exempttot', 'yearbuilt', 
                      'yearalter1', 'yearalter2', 'histdist', 'landmark', 'builtfar', 'residfar', 'commfar', 
                      'facilfar', 'condono']

# Create filters to select rows based on the selected options
filtered_df = df.copy() # Start with a copy of the original dataframe
block=0
lot=0
# Create form with user inputs
with st.sidebar:
    with st.form("address_form"):        
        selected_owner = st.selectbox('Select or type Owners name ',owners)
        selected_owner = selected_owner.strip().upper()
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Owner: ", selected_owner)
            filtered_df = filtered_df[(filtered_df['ownername'] == selected_owner)]

# Display the number of rows in the filtered dataframe
st.sidebar.write(f"Number of Properties: {filtered_df.shape[0]}")

#plotly 

fig = px.scatter_mapbox(filtered_df, lat="latitude", lon="longitude", hover_name="address", 
                        hover_data=["ownername",
                                    "block",
                                    "lot"],
                        zoom=15)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)

# Display the filtered dataframe with the specified columns
st.write(filtered_df[columns_to_display])
selected_owner = filtered_df['ownername'].values[0]

expander = st.expander("Owner Details")
expander.write(selected_owner)