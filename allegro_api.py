import secret
import requests, json
import subprocess
import sys
import logging
import time

token_url = "https://allegro.pl.allegrosandbox.pl/auth/oauth/token"

callback_uri = "http://localhost:8000"

test_api_url= "https://api.allegro.pl.allegrosandbox.pl"

get_sale_categories='/sale/categories'
get_sale_offers='/sale/offers'

logging.captureWarnings(True)


##
##    function to obtain a new OAuth 2.0 token from the authentication server
##
def get_new_token():

    print('getting token...')
    auth_server_url = token_url
    print(secret.clientsecret_coded)
    client_id = secret.client_ID
    client_secret = secret.client_secret

    token_req_payload = {'grant_type': 'client_credentials'}

    token_response = requests.post(auth_server_url,
                                   data=token_req_payload, verify=False, allow_redirects=False,
                                   auth=(client_id, client_secret))
    print('token response status: ', token_response.status_code)
    if token_response.status_code != 200:
        print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
        sys.exit(1)
    else:
        print("Successfully obtained a new token")
        tokens = json.loads(token_response.text)
        return tokens['access_token']

##
## 	obtain a token before calling the API for the first time
## 	the token is valid for 15 minutes
##
token = get_new_token()

if token == None:
    print('token is empty')
    exit()
print('token:',token)
##
##   call the API with the token
##
#api_call_headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.allegro.public.v1+json'}
headers = {}
headers['Content-type'] = 'application/vnd.allegro.public.v1+json'
headers['Accept'] = 'application/vnd.allegro.public.v1+json'
headers['Authorization'] = "Bearer {}".format(token)
api_call_response = requests.get(test_api_url+get_sale_offers, headers=headers, verify=False)
print('api call response: ', api_call_response)
print('api response json', api_call_response.json())
##
##