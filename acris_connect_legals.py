from streamlit.connections import ExperimentalBaseConnection
import requests 
import pandas as pd
import streamlit as st
from sodapy import Socrata

class AcrisConnectionLegal(ExperimentalBaseConnection):
    """ Class to connect and fetch data from ACRIS LEGAL API """

    def __init__(self, document_id):
        self.base_url = f'https://data.cityofnewyork.us/resource/8h5j-fqxa.json?document_id={document_id}'

    def _connect(self):
        """Connect to ACRIS LEGAL API and returns data"""
        url = self.base_url
        print(url)
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
            raise Exception("No data received from ACRIS LEGAL API.")

        df = pd.json_normalize(self.conn)
        
        return df
