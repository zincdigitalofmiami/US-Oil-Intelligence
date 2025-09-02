'''
Service for interacting with the USDA National Agricultural Statistics Service (NASS) API.
'''
import os
import json
import requests
import pandas as pd
from ..core.config import settings

def _get_nass_api_key() -> str | None:
    """Reads the usda-api-key from the secrets file."""
    secrets_path = os.path.join(settings.data_dir, "secrets.json")
    if not os.path.exists(secrets_path):
        return None
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)
        return secrets.get("usda-api-key")

def get_nass_data() -> dict | None:
    """
    Fetches data from the USDA NASS API.

    This function will fetch national-level data for soybean planting progress 
    as an example. The NASS API is complex, so the parameters can be expanded 
    greatly.

    See API documentation here: https://quickstats.nass.usda.gov/api
    """
    api_key = _get_nass_api_key()
    if not api_key:
        print("NASS API key not found. Skipping data fetch.")
        return {"warning": "NASS API key not found in data/secrets.json"}

    # Example parameters for fetching US Soybean Planting Progress for the current year
    # These can be customized to get different data.
    params = {
        'key': api_key,
        'source_desc': 'SURVEY',
        'sector_desc': 'CROPS',
        'group_desc': 'FIELD CROPS',
        'commodity_desc': 'SOYBEANS',
        'short_desc': 'SOYBEANS - PROGRESS, PLANTED',
        'agg_level_desc': 'NATIONAL',
        'year': '2024', # You might want to make this dynamic
        'format': 'JSON'
    }

    try:
        response = requests.get("http://quickstats.nass.usda.gov/api/api_GET/", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not fetch data from NASS API: {e}")
        return {"error": f"Could not fetch data from NASS API: {e}"}
    except json.JSONDecodeError:
        print(f"ERROR: Failed to decode JSON response from NASS API. Response text: {response.text}")
        return {"error": "Failed to decode JSON response from NASS API"}
