
# Replace with your app details
# api_key = "248d831e-ea54-494f-bf45-352a15edf79b"
# api_secret = "2n0rwoktxs"
# redirect_uri = "https://www.google.com"
import urllib.parse

client_id = "248d831e-ea54-494f-bf45-352a15edf79b"
redirect_uri = "https://www.google.com"

login_url = f"https://api.upstox.com/v2/login/authorization/dialog?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=code"

print("Go to this URL and login:")
print(login_url)

import requests

client_id = "248d831e-ea54-494f-bf45-352a15edf79b"
client_secret = "2n0rwoktxs"
redirect_uri = "https://www.google.com"
auth_code = input("Paste the 'code' from URL: ")

token_url = "https://api.upstox.com/v2/login/authorization/token"

payload = {
    "code": auth_code,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "grant_type": "authorization_code"
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(token_url, data=payload, headers=headers)
print("Access Token Response:", response.json())

