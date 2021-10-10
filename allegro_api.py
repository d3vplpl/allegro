import secret
import requests, json
import subprocess
import sys
import logging
import time

token_url = "https://allegro.pl.allegrosandbox.pl/auth/oauth/token"

callback_uri = "http://localhost:8000"

test_api_url = "https://api.allegro.pl.allegrosandbox.pl/sale/categories"

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
#token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJhbGxlZ3JvOmFwaTpvcmRlcnM6cmVhZCIsImFsbGVncm86YXBpOnByb2ZpbGU6d3JpdGUiLCJhbGxlZ3JvOmFwaTpzYWxlOm9mZmVyczp3cml0ZSIsImFsbGVncm86YXBpOmJpbGxpbmc6cmVhZCIsImFsbGVncm86YXBpOmNhbXBhaWducyIsImFsbGVncm86YXBpOmRpc3B1dGVzIiwiYWxsZWdybzphcGk6c2FsZTpvZmZlcnM6cmVhZCIsImFsbGVncm86YXBpOmJpZHMiLCJhbGxlZ3JvOmFwaTpvcmRlcnM6d3JpdGUiLCJhbGxlZ3JvOmFwaTphZHMiLCJhbGxlZ3JvOmFwaTpwYXltZW50czp3cml0ZSIsImFsbGVncm86YXBpOnNhbGU6c2V0dGluZ3M6d3JpdGUiLCJhbGxlZ3JvOmFwaTpwcm9maWxlOnJlYWQiLCJhbGxlZ3JvOmFwaTpyYXRpbmdzIiwiYWxsZWdybzphcGk6c2FsZTpzZXR0aW5nczpyZWFkIiwiYWxsZWdybzphcGk6cGF5bWVudHM6cmVhZCIsImFsbGVncm86YXBpOm1lc3NhZ2luZyJdLCJhbGxlZ3JvX2FwaSI6dHJ1ZSwiZXhwIjoxNjMzOTI5OTI2LCJqdGkiOiI0MmRiMzAwOS1mMzg0LTQ3YjAtODBjNC1iODQ2N2UxNzViM2QiLCJjbGllbnRfaWQiOiJiM2NhNGZiZDczMjg0NDI4YjBhMTE4MmEzMDdlOTdkZiJ9.NSBSXbfbY97gxs7FPGzFNFCZlzv9Qa9gK6alM_qEUU4G1xktrFvDwegwxWZjHrWVg7udfa16XMO0QMog3uqXm7QTlZIH0seO_70FSOWzdVhjylhGibhxx9EeD7v9oeFtEXLFqyOP_epTX9QpoiKcfCk4aDXJow6HvGPB5Rj_fXE-7BDU3iXycpekF5ZlgMPQtMafj6CtJ_zdGbDyNWPTaP1BXydRyXOprs3dBCZaXYb0-RUHGj2o7kUEpeE_lIhKoLqowodc0JXbFO9khUqNP1jTVPuHet_xVe9Zx1Ous3D2Ca8whkhU15OMp8E9f8qbnFs3GZoonQw4t4hJ3q45sooUaZ4vd7aiB-JsnI__rzhVmExDDABxGuUVOpEjqxgKxMJSXZYDbBUfpWJ5UrtGU-WxzDMOUOVFp4zSaG3zgKwyVmQ5dWHUIetrXuPIiuW97c6hhOyBVlVEoBO5FOx70BbGavMBqZFfdwMKn0hh5-rI5uy8PM9s21I-JKT9QTT8SNvISL2rSyPbLFsRSW1V7Q-3d3ZBS3r3L9iV2z9HxkXIakoal1XeUormYAkM9j0B7WeK1Il2atQhL50hKg443RFScmcUjfqh6CquzNYZ2WVzDK9_CyfyP00M50ZzKWFhP7lkgzHhfFEqSUg9S5NZIwUjf2teF8Lz6SsRMuv8T78'

if token == None:
    print('token is empty')
    exit()
print('token:',token)
##
##   call the API with the token
##
#api_call_headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.allegro.public.v1+json'}
headers = {}
headers['Accept'] = 'application/vnd.allegro.public.v1+json'
headers['Authorization'] = "Bearer {}".format(token)
api_call_response = requests.get(test_api_url, headers=headers, verify=False)
print('api call response: ', api_call_response)
print('api response json', api_call_response.json())
##
##