
import requests
import time

# Using a free, public geocoding service (Nominatim from OpenStreetMap).
# A production system should have a dedicated API key for a more robust service
# like Google Geocoding API and respect its terms of service.
GEOCODING_API_URL = "https://nominatim.openstreetmap.org/search"

def geocode_address(address: str):
    """
    Converts a string address or place name into latitude and longitude.

    Args:
        address: The address or name of the place to geocode (e.g., "MGM Grand, Las Vegas, NV").

    Returns:
        A dictionary with 'lat' and 'lng' or None if not found.
    """
    if not address:
        return None

    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'SoyIntelApp/1.0 (kirk@zincdigital.co)'
    }

    try:
        response = requests.get(GEOCODING_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()

        if results:
            location = results[0]
            return {
                "lat": float(location.get('lat')),
                "lng": float(location.get('lon'))
            }
        else:
            return None
    except requests.RequestException as e:
        print(f"Geocoding request failed for '{address}': {e}")
        return None
    except (ValueError, KeyError, IndexError):
        print(f"Failed to parse geocoding response for '{address}'")
        return None

if __name__ == '__main__':
    # Example usage
    print("Geocoding 'Bellagio, Las Vegas'...")
    location = geocode_address("Bellagio, Las Vegas")
    if location:
        print(f"  -> Success: Lat {location['lat']}, Lng {location['lng']}")
    else:
        print("  -> Failed.")

    # Rate limiting example
    time.sleep(1) 

    print("Geocoding 'Caesars Palace, Las Vegas'...")
    location = geocode_address("Caesars Palace, Las Vegas")
    if location:
        print(f"  -> Success: Lat {location['lat']}, Lng {location['lng']}")
    else:
        print("  -> Failed.")
