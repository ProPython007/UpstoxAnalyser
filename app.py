import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
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
        "accept": "application/json",
        "Api-Version": "2.0",
        "Authorization": f"Bearer {conf['access_token']}",
    }

    response = requests.get(url, headers=headers)
    json_response = response.json()

    return json_response


def get_investments_plot_by_price(data):
    labels = [name['company_name'] for name in data]
    values = [avg_price['average_price']*avg_price['quantity'] for avg_price in data]
    qts = [qt['quantity'] for qt in data]

    fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', title="<b>Investments per Company by Price Weightage:</b>")


    df1 = pd.DataFrame(list(zip(labels, values)), columns=['Companies -->', 'Amounts -->'])
    df1.sort_values(by=['Amounts -->'], inplace=True)
    fig2 = px.bar(
        df1,
        x = 'Amounts -->',
        y = 'Companies -->',
        orientation="h",
        title="<b>Investments per Company by Amount:</b>",
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=True))
    )

    df2 = pd.DataFrame(list(zip(labels, qts)), columns=['Companies -->', 'Quantity -->'])
    df2.sort_values(by=['Quantity -->'], inplace=True)
    fig3 = px.bar(
        df2,
        x = 'Quantity -->',
        y = 'Companies -->',
        orientation="h",
        title="<b>Shares per Company by Quantity:</b>",
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=True))
    )

    st.subheader('Distribution by Invested Amount')
    l, r = st.columns(2)
    with l:
        st.plotly_chart(fig1, use_container_width=True)
    with r:
        st.plotly_chart(fig3, use_container_width=True)

    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(f'Total Amount Invested: {sum(values):.2f} /-')


def get_wannabe_investments_plot_by_price(data):
    labels = [name['company_name'] for name in data]
    values = [price['last_price']*(10 - price['quantity']) for price in data]
    qts = [10 - qt['quantity'] for qt in data]

    fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', title="<b>Investments per Company by Price Weightage Required:</b>")


    df1 = pd.DataFrame(list(zip(labels, values)), columns=['Companies -->', 'Amounts -->'])
    df1.sort_values(by=['Amounts -->'], inplace=True)
    fig2 = px.bar(
        df1,
        x = 'Amounts -->',
        y = 'Companies -->',
        orientation="h",
        title="<b>Investments per Company by Amount Required:</b>",
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=True))
    )

    df2 = pd.DataFrame(list(zip(labels, qts)), columns=['Companies -->', 'Quantity -->'])
    df2.sort_values(by=['Quantity -->'], inplace=True)
    fig3 = px.bar(
        df2,
        x = 'Quantity -->',
        y = 'Companies -->',
        orientation="h",
        title="<b>Shares per Company by Quantity Required:</b>",
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=True))
    )

    st.subheader('Distribution by Amount Required')
    l, r = st.columns(2)
    with l:
        st.plotly_chart(fig1, use_container_width=True)
    with r:
        st.plotly_chart(fig3, use_container_width=True)

    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(f'Total Amount Required: {sum(values):.2f} /-')



response = st.experimental_get_query_params()
if 'code' in response:
    st.sidebar.markdown('In case of any errors: [restart-app](https://upstoxapi.streamlit.app)')
    login(response['code'][0])
    st.success('Login Successfull!')

    data = get_holdings()
    st.write(data)

    with st.expander('Show Holdings'):
        get_investments_plot_by_price(data['data'])
        st.markdown('##')
    
    with st.expander('Show Goals'):
        get_wannabe_investments_plot_by_price(data['data'])
        st.markdown('##')

else:
    connect()