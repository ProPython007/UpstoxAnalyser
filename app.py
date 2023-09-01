import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
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



@st.cache_resource
def setup_config():
    with open('config.json') as f:
        conf_file = json.load(f)

    response = st.experimental_get_query_params()
    st.write(response)

    if 'code' in response:
        code = response['code'][0]
        st.write(f'\ncode: {code}')

        conf_file['code'] = code

        url = "https://api-v2.upstox.com/login/authorization/token"

        headers = {
            "accept": "application/json",
            "Api-Version": "2.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "code": code,
            "client_id": conf_file['apiKey'],
            "client_secret": conf_file['secretKey'],
            "redirect_uri": conf_file['rurl'],
            "grant_type": "authorization_code",
        }

        response = requests.post(url, headers=headers, data=data)
        json_response = response.json()
        st.write(f'\njres: {json_response}')

        access_token = json_response['access_token']
        
        conf_file['access_token'] = access_token

        return conf_file, True
    
    else:
        uri = f"https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id={conf_file['apiKey']}&redirect_uri={conf_file['rurl']}"
        st.markdown(f'[Authorize with Upstox]({uri})')
        st.stop()


def get_profile(conf):
    url = 'https://api-v2.upstox.com/user/profile'
    
    headers = {
        "accept": "application/json",
        "Api-Version": "2.0",
        "Authorization": f"Bearer {conf['access_token']}",
    }

    response = requests.get(url, headers=headers)
    json_response = response.json()

    return json_response


def pnl(data):
    net_pnl = 0
    initial = sum([avg_price['average_price']*avg_price['quantity'] for avg_price in data])
    
    for pnl in data:
        net_pnl += pnl['pnl']

    current = initial + net_pnl

    per = (current - initial) / initial
    st.metric(label=f"NET PNL of Rs. {initial:.2f} /-", value=f"{current:.2f} /-", delta=f"{per*100:.2f}%")


def plot_pnl(data):
    labels = [name['company_name'] for name in data]
    values = [price['pnl'] for price in data]

    df1 = pd.DataFrame(list(zip(labels, values)), columns=['Companies -->', 'PNLs -->'])
    df1.sort_values(by=['PNLs -->'], inplace=True)
    fig1 = px.bar(
        df1,
        x = 'PNLs -->',
        y = 'Companies -->',
        orientation="h",
        title="<b>PNL per Company:</b>",
    )
    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=True))
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown(f'Net PNL: {sum(values):.2f} /-')



def get_holdings(conf):
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


def get_ltps(symbs, conf):
    to_fetch = ','.join(symbs)

    url = 'https://api-v2.upstox.com/market-quote/ltp' 
    
    headers = {
        "accept": "application/json",
        "Api-Version": "2.0",
        "Authorization": f"Bearer {conf['access_token']}",
    }
    params = {
        "symbol": to_fetch
    }

    response = requests.get(url, headers=headers, params=params)
    json_response = response.json()

    return json_response


def get_wannabe_investments_plot_by_price(data, symbs, quantity, conf):
    labels = []
    values = []
    qts = []
    for name in data:
        if name['company_name'] in symbs:
            labels.append(name['company_name'])
            values.append(name['last_price']*(quantity - name['quantity']) if (name['last_price']*(quantity - name['quantity'])) > 0 else 0)
            qts.append(quantity - name['quantity'] if (quantity - name['quantity']) > 0 else 0)
    
    extra_labels = set(symbs) - set(labels)
    if extra_labels:
        ltps = get_ltps(extra_labels, conf)

        for k, v in ltps['data']:
            if k in extra_labels:
                labels.append(k)
                values.append(quantity*v['last_price'])

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
    with r:
        st.plotly_chart(fig1, use_container_width=True)
    with l:
        st.plotly_chart(fig3, use_container_width=True)

    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(f'Total Amount Required: {sum(values):.2f} /-')



resume = False
st.sidebar.markdown('In case of any errors: [restart-app](https://upstoxapi.streamlit.app)')

conf, resume = setup_config()
if not resume:
    st.stop()

st.success('Login Successfull!')

data = get_holdings(conf)

profile = get_profile(conf)

st.header(f"Welcome {profile['data']['user_name']}")
pnl(data['data'])
plot_pnl(data['data'])
st.markdown('##')

with st.expander('Show Holdings'):
    get_investments_plot_by_price(data['data'])
    st.markdown('##')

st.subheader('Set Goals Here:')

symbs = st.multiselect(
    'Select The Appropriate Symbols:',
    options= [name['company_name'] for name in data['data']],
    default= [name['company_name'] for name in data['data']]
)
quantity = st.slider('Quantity(s) [ALL]:', 1, 100, value=10, step=1)

get_wannabe_investments_plot_by_price(data['data'], symbs, quantity, conf)
st.markdown('##')