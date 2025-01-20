from flask import Flask, render_template, jsonify
import folium
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)

class LocationService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://us1.locationiq.com/v1"
        
        # Cache the coordinates
        self.DHARAMPETH_COORDS = [21.1409684, 79.0624344]  # danger zone
        self.DHANTOLI_COORDS = [21.1339435, 79.0805662]    # safe zone
        
    def get_coordinates(self, location):
        """Get coordinates for a location using LocationIQ Geocoding API"""
        url = f"{self.base_url}/search.php"
        params = {
            "key": self.api_key,
            "q": location,
            "format": "json"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return [float(data[0]["lat"]), float(data[0]["lon"])]
        return None

    def get_directions(self, start_coords, end_coords):
        """Get directions between two points using LocationIQ Directions API"""
        url = f"{self.base_url}/directions/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
        params = {
            "key": self.api_key,
            "steps": "true",
            "alternatives": "true",
            "geometries": "geojson"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

class SafetyNavigator:
    def __init__(self, location_service):
        self.location_service = location_service
        self.danger_zones = [
            {
                "name": "Dharampeth",
                "coords": location_service.DHARAMPETH_COORDS,
                "radius": 500  # meters
            }
        ]
        self.safe_zones = [
            {
                "name": "Dhantoli",
                "coords": location_service.DHANTOLI_COORDS,
                "radius": 500  # meters
            }
        ]

    def is_in_danger_zone(self, user_coords):
        """Check if user is in any danger zone"""
        from math import radians, sin, cos, sqrt, atan2

        def haversine_distance(coord1, coord2):
            R = 6371000  # Earth's radius in meters
            lat1, lon1 = radians(coord1[0]), radians(coord1[1])
            lat2, lon2 = radians(coord2[0]), radians(coord2[1])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c

        for zone in self.danger_zones:
            if haversine_distance(user_coords, zone["coords"]) <= zone["radius"]:
                return True
        return False

    def get_safe_routes(self, start_coords):
        """Get safe routes to nearest safe zone"""
        routes = self.location_service.get_directions(start_coords, self.safe_zones[0]["coords"])
        return routes

# Initialize services
location_service = LocationService("pk.aa93da0cec5f10d59f322b3a1c2c4029")
safety_navigator = SafetyNavigator(location_service)

# Simulated user location (in danger zone)
USER_LOCATION = location_service.DHARAMPETH_COORDS

@app.route('/')
def index():
    # Create map centered between danger and safe zones
    center_lat = (location_service.DHARAMPETH_COORDS[0] + location_service.DHANTOLI_COORDS[0]) / 2
    center_lon = (location_service.DHARAMPETH_COORDS[1] + location_service.DHANTOLI_COORDS[1]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Add danger zone
    folium.Circle(
        location=location_service.DHARAMPETH_COORDS,
        radius=500,
        color='red',
        fill=True,
        popup='Danger Zone - Dharampeth',
        tooltip='Danger Zone'
    ).add_to(m)

    # Add safe zone
    folium.Circle(
        location=location_service.DHANTOLI_COORDS,
        radius=500,
        color='green',
        fill=True,
        popup='Safe Zone - Dhantoli',
        tooltip='Safe Zone'
    ).add_to(m)

    # Add user marker
    folium.Marker(
        location=USER_LOCATION,
        popup='Your Location',
        tooltip='You are here',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # Get and display routes
    routes_data = safety_navigator.get_safe_routes(USER_LOCATION)
    
    if routes_data and 'routes' in routes_data:
        # Primary route (green)
        route_coords = routes_data['routes'][0]['geometry']['coordinates']
        folium.PolyLine(
            locations=[[coord[1], coord[0]] for coord in route_coords],
            color='green',
            weight=4,
            popup='Shortest Safe Route',
            tooltip='Primary Route'
        ).add_to(m)

        # Alternative route (blue) if available
        if len(routes_data['routes']) > 1:
            alt_route_coords = routes_data['routes'][1]['geometry']['coordinates']
            folium.PolyLine(
                locations=[[coord[1], coord[0]] for coord in alt_route_coords],
                color='blue',
                weight=4,
                popup='Alternative Safe Route',
                tooltip='Alternative Route'
            ).add_to(m)

    # Add route toggle control
    route_toggle = '''
    <div style="position: fixed; 
                bottom: 50px; 
                right: 50px; 
                z-index: 1000;">
        <select id="routeToggle" onchange="toggleRoute(this.value)" 
                style="padding: 10px; 
                       border-radius: 5px; 
                       background: white; 
                       border: 2px solid #ccc;">
            <option value="primary">Primary Route</option>
            <option value="alternative">Alternative Route</option>
        </select>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(route_toggle))

    # Add danger zone alert if user is in danger zone
    if safety_navigator.is_in_danger_zone(USER_LOCATION):
        alert_html = '''
        <div style="position: fixed; 
                    top: 10px; 
                    left: 50px; 
                    width: 300px; 
                    z-index: 9999; 
                    background-color: #ff4444; 
                    color: white; 
                    padding: 10px; 
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            ⚠️ You are in a danger zone. Calculating safest routes to safe zone.
        </div>
        '''
        m.get_root().html.add_child(folium.Element(alert_html))

    return m._repr_html_()

@app.route('/update_location/<float:lat>/<float:lon>')
def update_location(lat, lon):
    """API endpoint to update user location"""
    global USER_LOCATION
    USER_LOCATION = [lat, lon]
    is_danger = safety_navigator.is_in_danger_zone(USER_LOCATION)
    return jsonify({
        "in_danger": is_danger,
        "message": "You are in a danger zone!" if is_danger else "You are in a safe area."
    })

if __name__ == '__main__':
    app.run(debug=True)