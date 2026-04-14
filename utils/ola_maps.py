import requests
from django.conf import settings


class OlaMapsService:
    def __init__(self):
        self.client_id = settings.OLA_CLIENT_ID
        self.client_secret = settings.OLA_CLIENT_SECRET
        self.api_key = getattr(settings, 'OLA_API_KEY', settings.OLA_CLIENT_ID)  # Use API key for routing
        self.base_url = settings.OLA_API_BASE_URL
        self._access_token = None

    def get_access_token(self):
        if self._access_token:
            return self._access_token

        url = f"{self.base_url}/auth/v1/token"
        payload = {
            "grant_type": "client_credentials",
            "scope": "openid",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            self._access_token = response.json().get("access_token")
            return self._access_token
        except Exception as e:
            print(f"Ola Maps Token Error: {e}")
            return None

    def geocode(self, address):
        token = self.get_access_token()
        if not token:
            return None

        url = f"{self.base_url}/places/v1/geocode"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"address": address}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "geocoding" in data and data["geocoding"]:
                geom = data["geocoding"][0].get("geometry", {})
                location = geom.get("location", {})
                return {
                    "lat": location.get("lat"),
                    "lng": location.get("lng"),
                    "formatted_address": data["geocoding"][0].get("formatted_address")
                }
            return None
        except Exception as e:
            print(f"Ola Geocode Error: {e}")
            return None

    def reverse_geocode(self, lat, lng):
        token = self.get_access_token()
        if not token:
            return None

        url = f"{self.base_url}/places/v1/reverse-geocode"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"latlng": f"{lat},{lng}"}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and data["results"]:
                result = data["results"][0]
                return {
                    "formatted_address": result.get("formatted_address"),
                    "place_id": result.get("place_id")
                }
            return None
        except Exception as e:
            print(f"Ola Reverse Geocode Error: {e}")
            return None

    def autocomplete(self, input_text):
        token = self.get_access_token()
        if not token:
            return []

        url = f"{self.base_url}/places/v1/autocomplete"
        headers = {"Authorization": f"Bearer {token}"}
        # Location bias: Mathura-Vrindavan area (27.5, 77.7) with 50km radius
        params = {
            "input": input_text,
            "location": "27.5,77.7",
            "radius": "50000"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            predictions = []
            seen_coords = set()
            
            for p in data.get("predictions", []):
                description = p.get("description", "")
                description_parts = [part.strip() for part in description.split(",") if part.strip()]
                place_name = description_parts[0] if description_parts else description
                secondary_text = ", ".join(description_parts[1:]) if len(description_parts) > 1 else ""
                place_id = p.get("place_id")
                
                if "geometry" in p and "location" in p["geometry"]:
                    loc = p["geometry"]["location"]
                    lat, lng = loc.get("lat"), loc.get("lng")
                    
                    if lat and lng:
                        coord_key = (round(lat, 6), round(lng, 6))
                        if coord_key not in seen_coords:
                            seen_coords.add(coord_key)
                            predictions.append({
                                "description": description,
                                "place_name": place_name,
                                "secondary_text": secondary_text,
                                "lat": lat,
                                "lng": lng,
                                "place_id": place_id
                            })
                
                if len(predictions) >= 5:
                    break
            
            return predictions
        except Exception as e:
            print(f"Ola Autocomplete Error: {e}")
            return []

    def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
        # Use API key authentication for Directions API (not Bearer token)
        url = f"{self.base_url}/routing/v1/directions"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "api_key": self.api_key
        }
        headers = {
            "X-Request-Id": f"route_{origin_lat}_{origin_lng}_{dest_lat}_{dest_lng}".replace(".", "_")
        }

        try:
            response = requests.post(url, headers=headers, params=params, timeout=10)
            print(f"DEBUG Ola API status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"DEBUG Ola API response: {data}")

            if "routes" in data and data["routes"]:
                route = data["routes"][0]
                leg = route.get("legs", [{}])[0]
                distance_m = leg.get("distance", 0)
                duration_s = leg.get("duration", 0)
                print(f"DEBUG Ola route found: {distance_m}m, {duration_s}s")
                return {
                    "distance_km": distance_m / 1000,
                    "duration_minutes": duration_s / 60,
                    "geometry": route.get("overview_polyline"),
                    "steps": leg.get("steps", [])
                }
            print(f"DEBUG Ola no routes in response")
            return None
        except Exception as e:
            print(f"Ola Route Error: {e}")
            if 'response' in locals():
                print(f"DEBUG Ola error response: {response.text[:500]}")
            return None


ola_maps = OlaMapsService()
