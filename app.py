import streamlit as st
import urllib.parse
import pandas as pd
import requests
import json



# Settings:
## Extra CSS:
st.set_page_config(page_title='Upstox Portfolio Viewer', page_icon=':bar_chart:', layout='wide')
hide_st_style = '''
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_st_style, unsafe_allow_html=True)



def connect():
    conf = get_details()
    redirect_url = urllib.parse.quote(conf['rurl'], safe='')
    uri = f"https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id={conf['apiKey']}&redirect_uri={redirect_url}"

    st.markdown(f'[Authorize with Upstox]({uri})')


def login(code):
    conf = get_details()
    conf['code'] = code

    url = "https://api-v2.upstox.com/login/authorization/token"

    headers = {
        "accept": "application/json",
        "Api-Version": "2.0",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "code": conf['code'],
        "client_id": conf['apiKey'],
        "client_secret": conf['secretKey'],
        "redirect_uri": conf['rurl'],
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        json_response = response.json()
        access_token = json_response['access_token']
        conf['access_token'] = access_token
    except Exception:
        pass

    return conf


def get_details():
    with open('config.json') as f:
        data = json.load(f)
    return data


# def store_details(conf):
#     with open('config.json', 'w') as f:
#         json.dump(conf, f)


def get_holdings(conf):
    url = 'https://api-v2.upstox.com/portfolio/long-term-holdings'
    
    headers = {
        "accept": "application/json",
        "Api-Version": "2.0",
        "Authorization": f"Bearer {conf['access_token']}",
    }

    response = requests.get(url, headers=headers)
    json_response = response.json()
    st.write(json_response)



response = st.experimental_get_query_params()
if 'code' in response:
    conf = login(response['code'][0])
    if not conf:
        st.stop()
    st.success('Login Successfull!')

    holdings = st.button('Show Holdings')
    if holdings:
        st.write(get_holdings(conf))

else:
    connect()