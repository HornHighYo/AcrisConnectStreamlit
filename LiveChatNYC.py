# -*- coding: utf-8 -*-
"""
ACRIS_APP.PY

"""

import streamlit as st
from streamlit.connections import ExperimentalBaseConnection
import requests 
import pandas as pd
from acris_connect_realproperty import AcrisConnectionRP
from acris_connect_legals import AcrisConnectionLegal
import numpy as np
import plotly.express as px

st.set_page_config(page_title="chatNYC")
st.title("chatNYC")
st.sidebar.title("chatNYC")

#data

file_path="data/pluto_testAug26v3.xlsx"

df=pd.read_excel(file_path)


#streamlit mapping
st.title("streamlit mapping")
st.map(df, size='10')
st.dataframe(df)


#plotly 
st.title('plotly mapping')

fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", hover_name="address", 
                        hover_data=["ownername",
                                    "block",
                                    "lot"],
                        zoom=14)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)

    
st.dataframe(df)


#openai_api_key=st.secrets["openai"]["openai_api_key"]

# SEARCH ACRIS - REAL PROPERTY MASTER https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj

with st.form('my_form'):
  document = st.selectbox('Choose a document type', ['DEED', 'MTGE','AGMT'])
  submitted = st.form_submit_button('Submit')
 
  #FOR TESTING WITH SPYDER
  #submitted=True
  #document='AGMT'
  
  if submitted:
    # load data
    #conn = st.experimental_connection("acris_datasets", type=AcrisConnection)
    #df = conn.get(recorded_borough=borough, doc_type=document)
    conn = AcrisConnectionRP(document)
    conn._connect()
    df = conn.to_dataframe()
   
    st.write('Recent transactions:')
    #st.dataframe(df.head(20))
    # Sort the dataframe by 'document_amount' in descending order
    df['document_amt'] = df['document_amt'].astype(float).round().astype(int)
    df_sorted = df.sort_values(by='document_amt', ascending=False)
    
    # Select the top 10 rows
    df_top10 = df_sorted.head(10)
    df_top10.reset_index(inplace=True)
    del df_top10['index']
    #SEARCH ACRIS - Real Property Legals  https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Legals/8h5j-fqxa
    
    def get_address_info(row):
        conn2 = AcrisConnectionLegal(row['document_id'])
        conn2._connect()
        dflegal = conn2.to_dataframe()
        return pd.Series(dflegal.iloc[0])

    df_address_info = pd.DataFrame(columns=['document_id', 'borough', 'street_number', 'street_name', 'block', 'lot'])
        
    for index, row in df_top10.iterrows():
          try:
              conn2 = AcrisConnectionLegal(row['document_id'])
              conn2._connect()
              df_legal = conn2.to_dataframe()
              selected_columns = ['document_id', 'borough','street_number', 'street_name', 'block', 'lot']
              df_legal = df_legal[selected_columns]
              df_address_info = pd.concat([df_address_info, df_legal.iloc[0:1]])
              #df_address_info = df_address_info.append(df_legal.iloc[0])
              print('df_address_info ', df_address_info)
          except Exception as e:
              st.error(f"Could not get address info for Document ID {row['document_id']}: {e}")
              # set up placeholder for df_legal if there is an error
              placeholder_dict = {"document_id": "", "borough": "", "street_number": "", "street_name": "", "block": "", "lot": ""} # replace "column1", "column2", etc. with your actual column names
              df_legal = pd.DataFrame(placeholder_dict, index=[0])
              df_address_info = df_address_info.append(df_legal)
            
    # append the new columns to df_top10
    df_top10 = pd.merge(df_top10.reset_index(drop=True), df_address_info.reset_index(drop=True), left_index=True, right_index=True, suffixes=('','_y'))
       
    # Select the desired columns only
    selected_columns = ['document_amt','street_number','street_name','document_date','document_id', 'doc_type', 'block','lot','borough']
    df_top10 = df_top10[selected_columns]
    
    # Display the dataframe
    st.dataframe(df_top10.sort_values(by='document_amt', ascending=False))
