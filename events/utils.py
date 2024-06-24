# Import necessary modules
import requests
from django.conf import settings

# Function to convert a location name into latitude and longitude coordinates
def geocode_location(location):
    # Get the API key from the project settings
    api_key = settings.OPENCAGE_API_KEY
    # Base URL for the OpenCage Geocoding API
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    
    # Prepare the parameters for the API request
    params = {
        'q': location,  # The location to geocode
        'key': api_key,  # Your API key
        'limit': 1,  # Limit to one result
    }
    
    # Send a GET request to the API
    response = requests.get(base_url, params=params)
    
    # Parse the JSON response
    results = response.json()
    
    # Check if we got any results
    if results and results['results']:
        # Extract the latitude and longitude from the first result
        location = results['results'][0]['geometry']
        return location['lat'], location['lng']
    
    # If no results were found, return None for both latitude and longitude
    return None, None