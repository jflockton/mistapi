from dotenv import load_dotenv
load_dotenv()
import sys
import os
import requests
import json

OUTPUT_DIR = "./outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

API_URL = os.getenv("API_URL").strip()
API_KEY = os.getenv("MIST_API_KEY")
site_uksecmkps = os.getenv("site_uksecmkps")

url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_uksecmkps}/devices"
headers = {
    "Authorization": f"Token {API_KEY}",
    "Accept": "application/json"
}
params = {
    "type": "switch",
    "limit": 100,
    "page": 1
}

response = requests.get(url, headers=headers, params=params)
print("Status code:", response.status_code)

try:
    devices = response.json()
    if devices:
        for device in devices:
            device_id = device.get('id')
            device_name = device.get('name', 'unknown_device').replace(" ", "_")
            print(f"Name: {device_name}")
            print(f"ID: {device_id}\n")
            # Fetch device info
            device_url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_uksecmkps}/devices/{device_id}"
            device_response = requests.get(device_url, headers=headers)
            device_info = device_response.json()
            # Save to file
            filename = f"{OUTPUT_DIR}/{site_uksecmkps}_{device_name}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(device_info, indent=4))
    else:
        print("No switches found.")
except Exception as e:
    print("Could not decode JSON. Raw response:")
    print(response.text)
    print(f"Error: {e}")