from streamlit.connections import ExperimentalBaseConnection
import requests 
import pandas as pd
#import streamlit as st
#from sodapy import Socrata

class AcrisConnectionRP(ExperimentalBaseConnection):
    """ Class to connect and fetch data from ACRIS API """

    def __init__(self, doc_type):
        #self.base_url = f"https://data.cityofnewyork.us/resource/bnx9-e6tj.json?$where=document_date>='2023-06-01T00:00:00'&recorded_borough={recorded_borough}&doc_type={doc_type}"
        self.base_url = f"https://data.cityofnewyork.us/resource/bnx9-e6tj.json?$where=document_date>='2023-06-01T00:00:00'&doc_type={doc_type}"
    def _connect(self):
        """Connect to ACRIS API and returns data"""
        url = self.base_url
        #print(url)
        headers = {
             "User-Agent": "Declared-Bot/1.0"
        }
        try:  
            response = requests.get(url, headers=headers).json()
        except ValueError:  
            raise Exception("Invalid JSON response")

        if "error" in response:
            raise Exception(f"Error from Edgar API: {response['error']}")

        self.conn = response
    
    def to_dataframe(self):
        """Convert the API data to pandas DataFrame"""
        if not self.conn:
            raise Exception("No data received from ACRIS API.")

        df = pd.json_normalize(self.conn)
        
        return df
