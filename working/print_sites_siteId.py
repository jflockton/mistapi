from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json

API_URL = os.getenv("API_URL").strip()
API_KEY = os.getenv("MIST_API_KEY")
ORG_ID = os.getenv("ORG_ID")

url = f"{API_URL.rstrip('/')}/api/v1/orgs/{ORG_ID}/sites"
headers = {"Authorization": f"Token {API_KEY}"}
response = requests.get(url, headers=headers)
print("Status code:", response.status_code)
try:
    sites = response.json()
    for site in sites:
        print(f"Name: {site.get('name')} | ID: {site.get('id')}")
except Exception as e:
    print("Could not decode JSON. Raw response:")
    print(response.text)
    print(f"Error: {e}")