# ---------------------------
# Private keys
# ---------------------------

import base64
import json

with open('secret.json') as json_file:
    data = json.load(json_file)

api_key = data["api_key"]
secret = data["secret"]


base64DataBytes = base64.b64encode((api_key + ':' + secret).encode("utf-8"))
base64Data = str(base64DataBytes, "utf-8")

# ---------------------------
# Request OAuthToken
# ---------------------------

import requests as req

host = 'https://api.idealista.com'
url = host + '/oauth/token'
headers = {
            'Authorization': 'Basic ' + base64Data,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
params = {
    'grant_type': 'client_credentials',
    'scope': 'read'
}

response = req.post(url, params=params, headers=headers)

token = response.json()
headers['Authorization'] = token['token_type'] + ' ' + token['access_token']

# ---------------------------
# Request Idealista Data
# ---------------------------

country = 'pt'
center = (38.715663,-9.147070)

params = {
    'operation': 'sale',
    'propertyType': 'homes',
    'center': str(center[0]) + ',' + str(center[1]),
    'distance': 10000,
    'locale': 'pt',
    'sinceDate': 'Y', #  last 2 days - W:last week, M: last month, T:last day (for rent except rooms), Y: last 2 days (sale and rooms)
    'minSize': 100,
    #'maxPrice': 650000,
    'maxItems': 50
}
url = host + '/3.5/' + country + '/search'
#response = req.post(url, params=params, headers=headers)

totalPages = -1
numPage = 1
response = []
while(numPage != totalPages+1):
    params['numPage'] = numPage
    resp_obj = req.post(url, params=params, headers=headers)
    if(resp_obj.status_code != req.codes.ok):
        print("FAILED REQUEST:")
        print(resp_obj.status_code)
        print(resp_obj.text)
        print("----------------------------------")
        print("----------------------------------")
        print(json.dumps(response))
        exit(1)
    response.append(resp_obj.json())
    totalPages = response[-1]['totalPages']
    numPage += 1

# ---------------------------
# Save response json
# ---------------------------

from datetime import datetime
import json

time_format = '%d-%m-%Y_%H:%M:%S'
data_path = './data'

now = datetime.now()
s2 = now.strftime(time_format)

json = json.dumps(response)
f = open(data_path + '/' + s2 + ".json","w")
f.write(json)
f.close()
