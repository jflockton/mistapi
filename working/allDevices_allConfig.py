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
ORG_ID = os.getenv("ORG_ID")

def get_sites():
    url = f"{API_URL.rstrip('/')}/api/v1/orgs/{ORG_ID}/sites"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_switches(site_id):
    url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices"
    headers = {"Authorization": f"Token {API_KEY}"}
    all_switches = []
    page = 1
    while True:
        params = {
            "type": "switch",
            "limit": 300,
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        switches = response.json()
        if not switches:
            break
        all_switches.extend(switches)
        page += 1
    return all_switches

def get_device_info(site_id, device_id):
    url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices/{device_id}"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    try:
        sites = get_sites()
        for site in sites:
            site_id = site.get('id')
            site_name = site.get('name', 'unknown_site').replace(" ", "_")
            print(f"Processing site: {site_name} ({site_id})")
            try:
                switches = get_switches(site_id)
                if not switches:
                    print(f"  No switches found for site {site_name}")
                    continue
                for switch in switches:
                    device_id = switch.get('id')
                    device_name = switch.get('name', 'unknown_switch').replace(" ", "_")
                    print(f"  Fetching config for switch: {device_name} ({device_id})")
                    try:
                        device_info = get_device_info(site_id, device_id)
                        filename = f"{OUTPUT_DIR}/{site_name}_{device_name}.txt"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(json.dumps(device_info, indent=4))
                    except Exception as e:
                        print(f"    Failed to fetch/save config for switch {device_id}: {e}")
            except Exception as e:
                print(f"  Failed to fetch switches for site {site_id}: {e}")
    except Exception as e:
        print(f"Failed to fetch sites: {e}")

if __name__ == "__main__":
    main()