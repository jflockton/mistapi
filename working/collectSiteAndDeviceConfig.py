from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json

OUTPUT_DIR = "./outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

API_URL = os.getenv("API_URL").strip()
API_KEY = os.getenv("MIST_API_KEY")

def get_sites():
    url = f"{API_URL.rstrip('/')}/api/v1/sites"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_devices(site_id):
    url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_device_info(site_id, device_id):
    url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices/{device_id}"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    try:
        # Step 1: List sites
        sites = get_sites()
        print("Available Sites:")
        for idx, site in enumerate(sites, 1):
            print(f"{idx}: {site['name']} (ID: {site['id']})")
        site_choice = int(input("Select a site by number: ")) - 1
        site_id = sites[site_choice]['id']

        # Step 2: List devices in site
        devices = get_devices(site_id)
        print("\nDevices in selected site:")
        for idx, device in enumerate(devices, 1):
            print(f"{idx}: {device.get('name', 'Unnamed')} (ID: {device['id']})")
        device_choice = int(input("Select a device by number: ")) - 1
        device_id = devices[device_choice]['id']

        # Step 3: Fetch and save device config
        device_info = get_device_info(site_id, device_id)
        device_name = device_info.get('name', 'unknown_device').replace(" ", "_")
        filename = f"{OUTPUT_DIR}/{device_name}.log"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(device_info, indent=4))
        print(f"\nDevice configuration saved to {filename}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()