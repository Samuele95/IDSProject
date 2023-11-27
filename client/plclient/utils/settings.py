import streamlit as st
import pandas as pd
import random
import string

backend_url = 'http://127.0.0.1:8000/'
users_endpoint = backend_url+'users/'
shops_endpoint = backend_url+'shops/'


@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    for splitted_df in df:
        splitted_df.insert(0, "Select", False)
    return df
