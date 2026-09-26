"""
google_places.py
────────────────
Service for interfacing with Google Places API (New).
Provides Text Search and Place Details with minimal, cost-conscious field masks.
"""

import os
import requests
from typing import Dict, Any, List, Optional

PLACES_API_BASE = "https://places.googleapis.com/v1"


def get_api_key(passed_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Google Places API key from param, env, or secrets."""
    if passed_key and passed_key.strip():
        return passed_key.strip()
    return os.environ.get("GOOGLE_PLACES_API_KEY", "").strip() or None


def search_places_text(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for places using Google Places API (New) Text Search.
    Uses a minimal field mask to minimize latency and billing cost.
    """
    key = get_api_key(api_key)
    if not key:
        return {
            "success": False,
            "error": "API_KEY_MISSING",
            "message": "Google Places API key is not configured. Please set the GOOGLE_PLACES_API_KEY environment variable or provide a key.",
            "places": []
        }

    if not query or not query.strip():
        return {
            "success": False,
            "error": "EMPTY_QUERY",
            "message": "Search query cannot be empty.",
            "places": []
        }

    url = f"{PLACES_API_BASE}/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.googleMapsUri"
    }
    payload = {
        "textQuery": query.strip(),
        "maxResultCount": 10
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            raw_places = data.get("places", [])
            places = []
            for p in raw_places:
                display_name = p.get("displayName", {}).get("text", "Unknown Place")
                places.append({
                    "place_id": p.get("id"),
                    "name": display_name,
                    "address": p.get("formattedAddress", ""),
                    "rating": p.get("rating"),
                    "user_rating_count": p.get("userRatingCount", 0),
                    "maps_uri": p.get("googleMapsUri", "")
                })
            return {
                "success": True,
                "places": places,
                "total_found": len(places)
            }
        elif response.status_code in [400, 401, 403]:
            err_data = response.json().get("error", {})
            return {
                "success": False,
                "error": "AUTHENTICATION_OR_PERMISSION_ERROR",
                "message": err_data.get("message", "Invalid API key, billing issue, or Google Places API not enabled on project."),
                "places": []
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "error": "QUOTA_EXCEEDED",
                "message": "Google Places API quota exceeded or rate limit reached.",
                "places": []
            }
        else:
            return {
                "success": False,
                "error": "API_ERROR",
                "message": f"Google Places API returned status code {response.status_code}.",
                "places": []
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "TIMEOUT",
            "message": "Google Places API request timed out. Please try again.",
            "places": []
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": "NETWORK_ERROR",
            "message": f"Network error communicating with Google Places API: {str(e)}",
            "places": []
        }


def get_place_details(place_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches Place Details and raw reviews using Google Places API (New).
    Uses explicit field mask for place info and reviews.
    """
    key = get_api_key(api_key)
    if not key:
        return {
            "success": False,
            "error": "API_KEY_MISSING",
            "message": "Google Places API key is not configured.",
            "place": None
        }

    if not place_id or not place_id.strip():
        return {
            "success": False,
            "error": "INVALID_PLACE_ID",
            "message": "Place ID must be provided.",
            "place": None
        }

    url = f"{PLACES_API_BASE}/places/{place_id.strip()}"
    headers = {
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "id,displayName,formattedAddress,rating,userRatingCount,reviews,googleMapsUri"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            display_name = data.get("displayName", {}).get("text", "Unknown Place")
            return {
                "success": True,
                "place": {
                    "place_id": data.get("id"),
                    "name": display_name,
                    "address": data.get("formattedAddress", ""),
                    "rating": data.get("rating"),
                    "user_rating_count": data.get("userRatingCount", 0),
                    "maps_uri": data.get("googleMapsUri", ""),
                    "reviews": data.get("reviews", [])
                }
            }
        elif response.status_code in [400, 401, 403]:
            err_data = response.json().get("error", {})
            return {
                "success": False,
                "error": "AUTHENTICATION_OR_PERMISSION_ERROR",
                "message": err_data.get("message", "Invalid API key, billing issue, or Google Places API not enabled on project."),
                "place": None
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "error": "INVALID_PLACE_ID",
                "message": f"Place ID '{place_id}' was not found. It may be invalid or the place may have closed.",
                "place": None
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "error": "QUOTA_EXCEEDED",
                "message": "Google Places API quota exceeded or rate limit reached. Please try again later.",
                "place": None
            }
        else:
            return {
                "success": False,
                "error": "DETAILS_FETCH_FAILED",
                "message": f"Failed to retrieve place details (Status: {response.status_code}).",
                "place": None
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "TIMEOUT",
            "message": "Request for place details timed out.",
            "place": None
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": "NETWORK_ERROR",
            "message": f"Network error retrieving place details: {str(e)}",
            "place": None
        }
