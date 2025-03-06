import requests
import json
import folium
from geopy.distance import geodesic
import webbrowser
import os


def get_public_ip():
    """Fetches the actual public IP address"""
    response = requests.get("https://api64.ipify.org?format=json")
    return response.json().get("ip")


def get_lat_lon():
    """Fetches latitude and longitude from public IP"""
    ip = get_public_ip()  # Get the actual public IP
    response = requests.get(f"http://ip-api.com/json/{ip}")
    data = response.json()
    return data.get("lat"), data.get("lon")


def find_nearby_hospitals(radius=5000, limit=10):
    """
    Find nearby hospitals using OpenStreetMap's Overpass API with real-time location.
    
    Parameters:
    radius (int): Search radius in meters (default: 5000m/5km)
    limit (int): Maximum number of results to return (default: 10)
    
    Returns:
    list: List of dictionaries containing hospital information
    """
    latitude, longitude = get_lat_lon()  # Get user's real-time location
    print(f"Detected Location: Latitude {latitude}, Longitude {longitude}")

    overpass_url = "https://overpass-api.de/api/interpreter"

    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{latitude},{longitude});
      way["amenity"="hospital"](around:{radius},{latitude},{longitude});
      relation["amenity"="hospital"](around:{radius},{latitude},{longitude});
      node["amenity"="clinic"](around:{radius},{latitude},{longitude});
      way["amenity"="clinic"](around:{radius},{latitude},{longitude});
      node["amenity"="doctors"](around:{radius},{latitude},{longitude});
      node["emergency"="yes"](around:{radius},{latitude},{longitude});
    );
    out center body;
    """

    try:
        response = requests.post(overpass_url, data={"data": overpass_query})
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Overpass API: {e}")
        return []

    hospitals = []
    user_location = (latitude, longitude)

    for element in data.get("elements", []):
        if element["type"] == "node":
            hospital_lat = element["lat"]
            hospital_lon = element["lon"]
        elif "center" in element:
            hospital_lat = element["center"]["lat"]
            hospital_lon = element["center"]["lon"]
        else:
            continue  

        hospital_location = (hospital_lat, hospital_lon)
        distance = geodesic(user_location, hospital_location).kilometers

        tags = element.get("tags", {})
        name = tags.get("name", "Unnamed Medical Facility")
        amenity_type = tags.get("amenity", "")
        emergency = "Yes" if tags.get("emergency") == "yes" else "No"
        phone = tags.get("phone", tags.get("contact:phone", "Not available"))

        hospitals.append({
            "name": name,
            "type": amenity_type.capitalize(),
            "latitude": hospital_lat,
            "longitude": hospital_lon,
            "distance_km": round(distance, 2),
            "emergency": emergency,
            "phone": phone,
            "address": tags.get("addr:full", f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip() or "Not available")
        })

    hospitals.sort(key=lambda x: x["distance_km"])
    return hospitals[:limit]


def generate_hospital_map(hospitals, filename="nearby_hospitals.html"):
    """
    Generate an interactive map with the user's location and nearby hospitals.
    
    Parameters:
    hospitals (list): List of hospital dictionaries
    filename (str): Output HTML file name
    
    Returns:
    str: Path to the generated map file
    """
    user_lat, user_lon = get_lat_lon()
    m = folium.Map(location=[user_lat, user_lon], zoom_start=13)

    folium.Marker(
        location=[user_lat, user_lon],
        popup="Your Location",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

    for hospital in hospitals:
        popup_text = f"""
        <b>{hospital['name']}</b><br>
        Type: {hospital['type']}<br>
        Distance: {hospital['distance_km']} km<br>
        Emergency: {hospital['emergency']}<br>
        Phone: {hospital['phone']}<br>
        Address: {hospital['address']}<br>
        <a href="https://www.google.com/maps/dir/{user_lat},{user_lon}/{hospital['latitude']},{hospital['longitude']}" target="_blank">Directions</a>
        """

        icon_color = "green" if hospital['emergency'] == "Yes" else "blue"

        folium.Marker(
            location=[hospital['latitude'], hospital['longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=icon_color, icon="plus")
        ).add_to(m)

    map_path = os.path.abspath(filename)
    m.save(map_path)
    return map_path


def run_hospital_finder():
    """Run hospital finder with real-time location detection."""
    print("\nFetching your location...")
    user_lat, user_lon = get_lat_lon()
    print(f"Your detected location: Latitude {user_lat}, Longitude {user_lon}")

    try:
        radius = int(input("\nEnter search radius in km (default 5): ") or "5") * 1000
    except ValueError:
        print("Invalid input, using default radius of 5 km.")
        radius = 5000

    print("\nSearching for nearby hospitals...")
    hospitals = find_nearby_hospitals(radius)

    if not hospitals:
        print("No hospitals found in the specified radius.")
        return

    print(f"\nFound {len(hospitals)} medical facilities:")
    for i, hospital in enumerate(hospitals, 1):
        print(f"\n{i}. {hospital['name']}")
        print(f"   Type: {hospital['type']}")
        print(f"   Distance: {hospital['distance_km']} km")
        print(f"   Emergency: {hospital['emergency']}")
        print(f"   Phone: {hospital['phone']}")
        print(f"   Address: {hospital['address']}")

    generate_map = input("\nGenerate interactive map? (y/n): ").lower()
    if generate_map == 'y':
        map_path = generate_hospital_map(hospitals)
        print(f"\nMap generated: {map_path}")

        open_map = input("Open map in browser? (y/n): ").lower()
        if open_map == 'y':
            webbrowser.open('file://' + map_path)


if __name__ == "__main__":
    run_hospital_finder()