from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json

API_URL = os.getenv("API_URL").strip()
API_KEY = os.getenv("MIST_API_KEY")
site_id = os.getenv("site_uksecmkps")
device_id = "00000000-0000-0000-1000-9c5a80ef1080"

# 1. Fetch current device config
get_url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices/{device_id}"
headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json"
}
response = requests.get(get_url, headers=headers)
response.raise_for_status()
device_config = response.json()

# 2. Update the networks section
if "networks" not in device_config:
    device_config["networks"] = {}

device_config["networks"]["jim-test"] = {
    "vlan_id": "3000",
    "subnet": "",
    "subnet6": ""
}

# 3. Push the update
put_url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices/{device_id}"
put_response = requests.put(put_url, headers=headers, data=json.dumps(device_config))
print("Status code:", put_response.status_code)
try:
    print("Response:", json.dumps(put_response.json(), indent=4))
except Exception as e:
    print("Raw response:", put_response.text)
    print(f"Error parsing JSON: {e}")