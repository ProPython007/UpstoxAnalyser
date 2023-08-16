import config as conf
import requests


url = "https://api-v2.upstox.com/login/authorization/token"

headers = {
    "accept": "application/json",
    "Api-Version": "2.0",
    "Content-Type": "application/x-www-form-urlencoded",
}

data = {
    "code": conf.code,
    "client_id": conf.apiKey,
    "client_secret": conf.secretKey,
    "redirect_uri": conf.rurl,
    "grant_type": "authorization_code",
}


response = requests.post(url, headers=headers, data=data)
json_response = response.json()
print(json_response)
access_token = json_response['access_token']
print(access_token)

