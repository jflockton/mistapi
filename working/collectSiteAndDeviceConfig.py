from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json

OUTPUT_DIR = "./outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Get your site and device info from .env ---
API_URL = os.getenv("API_URL").strip()
API_KEY = os.getenv("MIST_API_KEY")
site_id = os.getenv("site_uksecmkps")
device_id = "00000000-0000-0000-1000-9c5a80ef1080"  # Set your device ID here

def get_device_info(site_id, device_id):
    url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices/{device_id}"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    try:
        device_info = get_device_info(site_id, device_id)
        device_name = device_info.get('name', 'unknown_device').replace(" ", "_")
        filename = f"{OUTPUT_DIR}/{device_name}.log"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(device_info, indent=4))
        print(f"Device configuration saved to {filename}")
    except Exception as e:
        print(f"Failed to fetch/save device config: {e}")

if __name__ == "__main__":
    main()