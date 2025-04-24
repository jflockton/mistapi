from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json

API_URL = os.getenv("API_URL").strip()
API_KEY = os.getenv("MIST_API_KEY")
ORG_ID = os.getenv("ORG_ID")

def test_get_sites():
    url = f"{API_URL.rstrip('/')}/api/v1/orgs/{ORG_ID}/sites"
    headers = {
        "Authorization": f"Token {API_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("Response JSON:", json.dumps(response.json(), indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err} - Response: {response.text}")
    except Exception as err:
        print(f"Other error occurred: {err}")

if __name__ == "__main__":
    test_get_sites()