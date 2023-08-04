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

st.set_page_config(page_title="Acris Connect")
st.title("Acris Connect - Connect to NYC Property Information")
st.sidebar.title("My Submission to the Streamlit Connections Hackathon")
st.sidebar.write("Using Stremlit St.experimnetal_connection I built a connection to my favorite datasource = New York City Real Estate Data via Acris")
st.sidebar.title("Acris provides up-to-date information on recorded real estate transactions in NYC (every deed, mortgage and other recorded document")
st.sidebar.write("Utilizes two API's maintained by NYC OpenData to first search recently recorded documents.  https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj ")
st.sidebar.write("And then access the real property information to determine the relevant properties.  https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Legals/8h5j-fqxa ")
st.sidebar.title("This is only a taste of the insights that you can identify in this data (using the power of Streamlit, Pandas and Python)")
st.sidebar.title("follow me at https://twitter.com/HornHighYo1 and https://github.com/HornHighYo")

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

    df_address_info = pd.DataFrame()
        
    for index, row in df_top10.iterrows():
          try:
              conn2 = AcrisConnectionLegal(row['document_id'])
              conn2._connect()
              df_legal = conn2.to_dataframe()
              selected_columns = ['document_id', 'borough','street_number', 'street_name', 'block', 'lot']
              df_legal = df_legal[selected_columns]
              df_address_info = df_address_info.append(df_legal.iloc[0])
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
