# -*- coding: utf-8 -*-
"""
ACRIS_APP.PY

"""

import streamlit as st
import pandas as pd
#import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import sqlite3
import random
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

st.set_page_config(page_title="ChatNYC")
st.title("SEARCH by Property Details")
st.sidebar.title("SEARCH by Proprty Details")

#data

# @st.cache_data
# def load_data():
#     file_path="data/pluto_testAug29.xlsx"
#     df=pd.read_excel(file_path)
#     return df

# Create form with user inputs
boroughs=['MN','BX','BK','QN','SI']
with st.sidebar:
    selected_borough = st.selectbox('Select Borough', boroughs, index=boroughs.index('MN'))

@st.cache_data
def load_data(borough):
    conn = sqlite3.connect("data/NYCv1active.db")
    query = "SELECT * FROM pluto where borough = ? and zipcode = 10128"
    df = pd.read_sql_query(query, conn, params=[borough])
    return df

df = load_data(selected_borough)

# Create list of addresses for autocomplete
#addresses = df['address'].dropna().unique().tolist()
#addresses.insert(0, 'Enter Address')
#random_address = random.choice(addresses)

# Specify the columns to display in the filtered dataframe
columns_to_display = ['address', 'block', 'lot', 'zipcode','zonedist1', 'bldgclass', 'landuse',
                      'ownername', 'numfloors', 'unitsres', 'unitstotal', 'lotfront', 'lotdepth',
                      'bldgfront', 'bldgdepth',  'assessland', 'assesstot', 'exempttot', 'yearbuilt', 
                      'yearalter1', 'yearalter2', 'histdist', 'landmark', 'builtfar', 'residfar', 'commfar', 
                      'facilfar', 'condono','latitude','longitude','bbl']

# Create filters to select rows based on the selected options
filtered_df = df.copy() # Start with a copy of the original dataframe
#random='yes'

# Create dropdown menus with options for building class, borough, and zipcode
##selected_borough = st.sidebar.selectbox("Select Borough", ['All'] + list(df['borough'].unique()),index=1)
selected_zipcode = st.sidebar.selectbox("Select Zipcode", ['All'] + list(df['zipcode'].unique()),index=1)
selected_bldgclass = st.sidebar.selectbox("Select Building Class", ['All'] + list(df['bldgclass'].unique()))

# Create filters to select rows based on the selected options
filtered_df = df.copy() # Start with a copy of the original dataframe

if selected_bldgclass != 'All':
    filtered_df = filtered_df[filtered_df['bldgclass'] == selected_bldgclass]
    
if selected_borough != 'All':
    filtered_df = filtered_df[filtered_df['borough'] == selected_borough]
    
if selected_zipcode != 'All':
    filtered_df = filtered_df[filtered_df['zipcode'] == selected_zipcode]

# Display the number of rows in the filtered dataframe
st.sidebar.write(f"Number of Properties: {filtered_df.shape[0]}")

# Filter the dataframe for the specified columns
filtered_df = filtered_df[columns_to_display]

gb = GridOptionsBuilder.from_dataframe(filtered_df)
#gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
gb.configure_side_bar() #Add a sidebar
#gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection

gridOptions = gb.build()



grid_response = AgGrid(
     filtered_df,
     gridOptions=gridOptions,
     #data_return_mode='AS_INPUT', 
     #update_mode='MODEL_CHANGED', 
     fit_columns_on_grid_load=False,
     #theme='blue', #Add theme color to the table
     enable_enterprise_modules=True,
     height=350, 
     width=500,
     reload_data=False,
     custom_css={
             "#gridToolBar": {
                 "padding-bottom": "0px !important",
             }
         }
 )


#folium
m = folium.Map(location=[filtered_df.latitude.mean(), filtered_df.longitude.mean()], zoom_start=18, control_scale=True)
#m = folium.Map(location=['40.7826', '-73.9656'], zoom_start=16, control_scale=True)

#out = st_folium(m, height=500, width=725)

#m = folium.Map(location=[40.7826, 73.9656], zoom_start=15, control_scale=True)

#if submitted: 
# Create a feature group
fg = folium.FeatureGroup(name="Properties")

for index, property_ in df.iterrows():
    fg.add_child(
        folium.Marker(
            location=[property_["latitude"], property_["longitude"]],
            icon=folium.Icon(color="green", icon="info-sign"),
            popup=str(property_["bbl"]),
            tooltip=property_["address"]
        )
    )

for index, property_ in filtered_df.iterrows():
    fg.add_child(
        folium.Marker(
            location=[property_["latitude"], property_["longitude"]],
            icon=folium.Icon(color="blue", icon="star"),
            popup=str(property_["bbl"]),
            tooltip=property_["address"]
        )
    )

out = st_folium(
    m,
    feature_group_to_add=fg,
    height=500,
    width=725,
    returned_objects=["last_object_clicked_popup","last_object_clicked_tooltip"],
    return_on_hover=False,
)

st.write("Property:   ", out["last_object_clicked_tooltip"])

# try:
#     selected_bbl=int(out["last_object_clicked_popup"])
# except:
#     selected_bbl=(out["last_object_clicked_popup"])

if out["last_object_clicked_popup"]:
    selected_bbl = int(float(out["last_object_clicked_popup"]))  

else:
    selected_bbl = int(filtered_df['bbl'].astype(int).iloc[0])
    #selected_bbl = int(filtered_df.iloc[0])
    #selected_bbl=filtered_df["bbl"]
    
st.write('BBL  ', selected_bbl)
selected_owner=''

# Filter the DataFrame using the condition: df['bbl'] == selected_bbl
#if selected_bbl:
selected_df = df[df['bbl'] == selected_bbl]
selected_df = selected_df.loc[:, columns_to_display]
st.dataframe(selected_df)

expander = st.expander("Owner Details")
selected_owner = selected_df['ownername'].values[0]

expander.write(selected_owner)





