import streamlit as st
import urllib.parse
import pandas as pd
import requests
import json



def connect():
    conf = get_details()
    redirect_url = urllib.parse.quote(conf['rurl'], safe='')
    uri = f"https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id={conf['apiKey']}&redirect_uri={redirect_url}"

    st.markdown(f'[Authorize with Upstox]({uri})')


def login(code):
    conf = get_details()
    conf['code'] = code

    store_details(conf)

    conf = get_details()

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

    response = requests.post(url, headers=headers, data=data)
    json_response = response.json()
    try:
        access_token = json_response['access_token']
        conf['access_token'] = access_token
    except Exception:
        pass

    store_details(conf)
    authorize()


def authorize():
    conf = get_details()

    url = "https://api-v2.upstox.com/login/authorization/token"

    headers = {
        "Api-Version": "2.0"
    }

    data = {
        "client_id": conf['apiKey'],
        "redirect_uri": conf['rurl'],
    }

    requests.get(url, headers=headers, data=data)


def get_details():
    with open('config.json') as f:
        data = json.load(f)
    return data


def store_details(conf):
    with open('config.json', 'w') as f:
        json.dump(conf, f)


def get_holdings():
    conf = get_details()

    url = 'https://api-v2.upstox.com/portfolio/long-term-holdings'
    
    headers = {
        "Api-Version": "2.0"
    }

    data = {
        "code": conf['code'],
        "client_id": conf['apiKey'],
        "client_secret": conf['secretKey'],
        "redirect_uri": f"{conf['rurl']}/?loggedin=True",
        "grant_type": "authorization_code",
    }

    response = requests.get(url, headers=headers, data=data)
    json_response = response.json()
    st.write(json_response)



response = st.experimental_get_query_params()
if 'code' in response:
    login(response['code'][0])
    st.success('Login Successfull!')
    get_holdings()
else:
    connect()