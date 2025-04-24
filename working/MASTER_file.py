from dotenv import load_dotenv
load_dotenv()
import sys
import os
import requests
import json
import copy
from datetime import datetime

# Helper to get site ID by env var name
def get_site_id(site_name):
    return os.getenv(site_name)

API_URL = os.getenv("API_URL").strip()
API_KEY = os.getenv("MIST_API_KEY")
site_id = os.getenv("site_uksecmkps")  # or use get_site_id("site_uksecmkps")
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

# --- Backup step ---
backup_dir = "./backups"
os.makedirs(backup_dir, exist_ok=True)
switch_name = device_config.get("name", device_id).replace(" ", "_")
now = datetime.now()
time_str = now.strftime("%H%M_%d%m%y")  # e.g., 1651_240425
backup_filename = f"{backup_dir}/{time_str}_{switch_name}.bak"
with open(backup_filename, "w", encoding="utf-8") as f:
    f.write(json.dumps(device_config, indent=4))
print(f"Backup of current config saved to {backup_filename}")

# 2. Load the interfaces.json config
with open("interfaces.json", "r", encoding="utf-8") as f:
    new_config = json.load(f)

# 3. Prepare merged config for dry-run comparison
proposed_config = copy.deepcopy(device_config)

# Track if changes are detected
port_usages_changed = False
port_config_changed = False

# 4. Merge port_usages (add/update, don't remove existing) only if present in interfaces.json
if "port_usages" in new_config:
    existing_port_usages = device_config.get("port_usages", {})
    new_port_usages = new_config.get("port_usages", {})
    merged_port_usages = existing_port_usages.copy()
    for key, value in new_port_usages.items():
        if key not in existing_port_usages or existing_port_usages[key] != value:
            port_usages_changed = True
        merged_port_usages[key] = value
    proposed_config["port_usages"] = merged_port_usages
else:
    new_port_usages = {}

# 5. Merge port_config (add/update, don't remove existing) only if present in interfaces.json
if "port_config" in new_config:
    existing_port_config = device_config.get("port_config", {})
    new_port_config = new_config.get("port_config", {})
    merged_port_config = existing_port_config.copy()
    for iface, iface_config in new_port_config.items():
        if iface not in existing_port_config or existing_port_config[iface] != iface_config:
            port_config_changed = True
        merged_port_config[iface] = iface_config
    proposed_config["port_config"] = merged_port_config
else:
    new_port_config = {}

# 6. Compare and act
if not port_usages_changed and not port_config_changed:
    print("No changes would be made to the device configuration.")
else:
    print("The following changes would be made:")
    if port_usages_changed:
        print("port_usages changes:")
        print(json.dumps(new_port_usages, indent=4))
    if port_config_changed:
        print("port_config changes:")
        print(json.dumps(new_port_config, indent=4))

    # 7. PUT the merged config back to the device
    put_url = f"{API_URL.rstrip('/')}/api/v1/sites/{site_id}/devices/{device_id}"
    put_response = requests.put(put_url, headers=headers, data=json.dumps(proposed_config))
    print(f"Status code: {put_response.status_code}")
    if port_usages_changed:
        print("Confirmed: port_usages updated.")
    if port_config_changed:
        print("Confirmed: port_config updated.")