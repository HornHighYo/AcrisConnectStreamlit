# -*- coding: utf-8 -*-
"""
ACRIS_APP.PY

"""

import streamlit as st
import pandas as pd
#import numpy as np
import folium
from streamlit_folium import st_folium
#import plotly.express as px
import sqlite3
import random

st.set_page_config(page_title="ChatNYC")
st.title("SEARCH by Address or Block/Lot")
st.sidebar.title("SEARCH by Address or Block/Lot")

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
    #query = "SELECT * FROM pluto where borough = ? and zipcode = 10128"
    query = "SELECT borough, zipcode, address, bbl, block, lot, latitude, longitude, ownername  FROM pluto where borough = ?" 
    df = pd.read_sql_query(query, conn, params=[borough])
    return df

df = load_data(selected_borough)
zipcodes = df['zipcode'].dropna().astype(int).unique().tolist()
selected_zipcode = st.sidebar.selectbox("Select Zipcode", zipcodes, index=1)


# Create list of addresses for autocomplete
addresses = df['address'].dropna().unique().tolist()
#addresses.insert(0, 'Enter Address')
#random_address = random.choice(addresses)

# Specify the columns to display in the filtered dataframe
columns_to_display = ['borough', 'block', 'lot', 'address', 'zipcode','zonedist1', 'bldgclass', 'landuse',
                      'ownertype', 'ownername', 'numfloors', 'unitsres', 'unitstotal', 'lotfront', 'lotdepth',
                      'bldgfront', 'bldgdepth',  'assessland', 'assesstot', 'exempttot', 'yearbuilt', 
                      'yearalter1', 'yearalter2', 'histdist', 'landmark', 'builtfar', 'residfar', 'commfar', 
                      'facilfar', 'condono']

# Create filters to select rows based on the selected options
filtered_df = df.copy() # Start with a copy of the original dataframe
#random='yes'

# Create form wiht user inputs
with st.sidebar:
    with st.form("address_form"):        
        selected_address = st.selectbox('Address', addresses, key='k7', placeholder='Enter Address or Block Lot below',)
        selected_address = selected_address.strip().upper()
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Address", selected_address)
        
        filtered_df = filtered_df[(filtered_df['address'] == selected_address)]
        block = int(filtered_df['block'])
        lot = int(filtered_df['lot'])
        
            

# Create form with user inputs
with st.sidebar:
    with st.form("bl_form"):
        selected_block = int(st.text_input('Block', value=block,key='k2'))
        selected_lot = int(st.text_input('Lot', value=lot,key='k3'))
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("block", selected_block, "lot", selected_lot)
            filtered_df = df[(df['block'] == selected_block) & (df['lot'] == selected_lot)]


# Display the number of rows in the filtered dataframe
st.sidebar.write(f"Number of Properties: {filtered_df.shape[0]}")

zip_df = df[(df['zipcode'] == int(selected_zipcode))]

#folium
#m = folium.Map(location=[filtered_df.latitude.mean(), filtered_df.longitude.mean()], zoom_start=18, control_scale=True)
m = folium.Map(location=['40.7826', '-73.9656'], zoom_start=16, control_scale=True)

#out = st_folium(m, height=500, width=725)

#m = folium.Map(location=[40.7826, 73.9656], zoom_start=15, control_scale=True)

#if submitted: 
# Create a feature group
fg = folium.FeatureGroup(name="Properties")



for index, property_ in zip_df.iterrows():
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
#will need to pull up other data
#selected_df = selected_df.loc[:, columns_to_display]
st.dataframe(selected_df)

expander = st.expander("Owner Details")
selected_owner = selected_df['ownername'].values[0]

expander.write(selected_owner)





