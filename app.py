import streamlit as st
import urllib.parse
import pandas as pd
import requests
import json


@st.cache_data
def get_details():
    with open('config.json') as f:
        data = json.load(f)
    return data


def store_details(conf):
    with open('config.json', 'w') as f:
        json.dump(conf, f)


conf = get_details()
redirect_url = urllib.parse.quote(conf['rurl'], safe='')
uri = f"https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id={conf['apiKey']}&redirect_uri={redirect_url}"

# print(f'\nGOTO: {uri}\n')
# code = input('Enter the code here: ')
# conf['code'] = code
st.markdown(f'[Authorize with Upstox]({uri})')
response = st.experimental_get_query_params()
print(response)


# store_details(conf)