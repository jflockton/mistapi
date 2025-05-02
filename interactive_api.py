from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json
import sys

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

def get_devices(site_id):
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
        while True:
            # Step 1: List sites
            try:
                sites = get_sites()
            except Exception as e:
                print(f"Error fetching sites: {e}")
                continue

            print("Available Sites:")
            for idx, site in enumerate(sites, 1):
                print(f"{idx}: {site['name']}")
            print("0: Exit")
            site_choice_str = input("Select a site by number (0 to exit): ").strip()
            if not site_choice_str.isdigit():
                print("Invalid input. Please enter a number.")
                continue
            site_choice = int(site_choice_str)
            if site_choice == 0:
                print("Exiting.")
                return
            if not (1 <= site_choice <= len(sites)):
                print("Invalid selection. Try again.")
                continue
            site_id = sites[site_choice - 1]['id']

            while True:
                # Step 2: List devices in site
                try:
                    devices = get_devices(site_id)
                except Exception as e:
                    print(f"Error fetching devices: {e}")
                    break

                if not devices:
                    print("\nNo devices found in this site.")
                    break
                print("\nDevices in selected site:")
                for idx, device in enumerate(devices, 1):
                    print(f"{idx}: {device.get('name', 'Unnamed')}")
                print("0: Return to site menu")
                print("99: Exit")
                device_choice_str = input("Select a device by number (0 to return, 99 to exit): ").strip()
                if not device_choice_str.isdigit():
                    print("Invalid input. Please enter a number.")
                    continue
                device_choice = int(device_choice_str)
                if device_choice == 0:
                    break
                if device_choice == 99:
                    print("Exiting.")
                    sys.exit(0)
                if not (1 <= device_choice <= len(devices)):
                    print("Invalid selection. Try again.")
                    continue
                device_id = devices[device_choice - 1]['id']

                # Step 3: Fetch and save device config
                try:
                    device_info = get_device_info(site_id, device_id)
                    device_name = device_info.get('name', 'unknown_device').replace(" ", "_")
                    filename = f"{OUTPUT_DIR}/{device_name}.log"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(json.dumps(device_info, indent=4))
                    print(f"\nDevice configuration saved to {filename}")
                except Exception as e:
                    print(f"Error fetching or saving device config: {e}")
                    continue

                               # Step 4: Optionally upload config
                upload = input("Would you like to upload 'upload_config.json' to this device? (y/n): ").strip().lower()
                if upload == 'y':
                    try:
                        if not os.path.exists('upload_config.json'):
                            print("❌ File 'upload_config.json' does not exist.")
                            continue
                        if os.path.getsize('upload_config.json') == 0:
                            print("❌ File 'upload_config.json' is empty.")
                            continue
                        with open('upload_config.json', 'r', encoding='utf-8') as f:
                            try:
                                upload_data = json.load(f)
                            except json.JSONDecodeError as jde:
                                print(f"❌ File is not valid JSON: {jde}")
                                continue
                        if not isinstance(upload_data, dict):
                            print("❌ File JSON structure is not a dictionary/object. Upload aborted.")
                            continue
                        put_url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices/{device_id}"
                        print(f"➡️  PUT to API endpoint: {put_url}")
                        headers = {
                            "Authorization": f"Token {API_KEY}",
                            "Content-Type": "application/json"
                        }
                        put_response = requests.put(put_url, headers=headers, data=json.dumps(upload_data))
                        print(f"\n➡️  PUT data sent to device ID: {device_id} at endpoint: {put_url}")
                        if put_response.ok:
                            print(f"✅ PUT succeeded! Status code: {put_response.status_code}")
                        else:
                            print(f"❌ PUT failed! Status code: {put_response.status_code}")
                        try:
                            response_json = put_response.json()
                            print("API Response:", json.dumps(response_json, indent=4))
                            # Print a summary if possible
                            if "msg" in response_json:
                                print(f"➡️  API Message: {response_json['msg']}")
                            elif "message" in response_json:
                                print(f"➡️  API Message: {response_json['message']}")
                            elif "error" in response_json:
                                print(f"❌ API Error: {response_json['error']}")
                            else:
                                print("✅ PUT completed. See above for full API response.")
                        except Exception:
                            print("Raw response:", put_response.text)
                            print("⚠️  Could not decode JSON from API response.")
                    except Exception as e:
                        print(f"❌ Failed to upload config: {e}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    main()