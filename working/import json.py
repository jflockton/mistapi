import json

input_file = "vlans.txt"
output_file = "vlans.json"

vlans = {}

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) != 2:
            continue
        vlan_id, name = parts
        vlans[name] = {
            "vlan_id": vlan_id,
            "subnet": "",
            "subnet6": ""
        }

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(vlans, f, indent=4)

print(f"Converted {input_file} to {output_file} in JSON format.")