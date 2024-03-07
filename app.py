import pandas as pd
import numpy as np
# import googlemaps
from urllib.parse import urlencode
import sqlite3
import re
import streamlit as st 
from utils.process_ipg_data import process_ipg_data



file_upload = st.file_uploader('Choose a Pickup Detail Report', key=['.xlsx'])
if file_upload is None:
    st.write('No file is selected')
else:
    processed_df = process_ipg_data(file_upload)
    st.dataframe(processed_df)
    null_lat_lng = processed_df[processed_df['Latitude'].isnull()]
    st.write(null_lat_lng)
   