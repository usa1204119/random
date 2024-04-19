import requests
from django.shortcuts import render
import folium
from folium.plugins import AntPath
from scgraph.geographs.marnet import marnet_geograph

def input_view(request):
    return render(request, 'input.html')

def about_view(request):
    return render(request, 'about.html')    

def calculate_route(request):
    if request.method == 'POST':
        origin_country = request.POST.get('origin_country')
        origin_port = request.POST.get('origin_port')
        dest_country = request.POST.get('dest_country')
        dest_port = request.POST.get('dest_port')

        # Retrieve port coordinates using OpenCage Geocoding API
        origin_coords = get_coordinates(origin_port, origin_country)
        dest_coords = get_coordinates(dest_port, dest_country)

        if origin_coords is None or dest_coords is None:
            # Handle case where coordinates couldn't be retrieved
            return render(request, 'error.html')

        # Create a map centered at the origin port
        map_center = [origin_coords[0], origin_coords[1]]
        mymap = folium.Map(location=map_center, zoom_start=5)

        # Add port icons for the origin and destination ports
        origin_icon_url = 'https://fontawesome.com/icons/ship?f=classic&s=solid'
        dest_icon_url = 'https://fontawesome.com/icons/ship?f=classic&s=solid'

        # Add markers with custom icons for the origin and destination ports
        folium.Marker(
            [origin_coords[0], origin_coords[1]],
            icon=folium.features.CustomIcon(origin_icon_url, icon_size=(50, 50))
        ).add_to(mymap)

        folium.Marker(
            [dest_coords[0], dest_coords[1]],
            icon=folium.features.CustomIcon(dest_icon_url, icon_size=(50, 50))
        ).add_to(mymap)

        # Get the shortest path between the provided ports using marnet_geograph
        output = marnet_geograph.get_shortest_path(
            origin_node={"latitude": origin_coords[0], "longitude": origin_coords[1]},
            destination_node={"latitude": dest_coords[0], "longitude": dest_coords[1]}
        )

        # Create a line with arrows indicating the direction of the path
        path_points = [(point['latitude'], point['longitude']) for point in output['coordinate_path']]
        AntPath(locations=path_points, use_arrows=True, color='green').add_to(mymap)

        # Convert the map to HTML
        map_html = mymap._repr_html_()

        # Pass the map HTML to the template context
        context = {
            'map': map_html
        }

        # Render the template with the context
        return render(request, 'map.html', context)
    else:
        # Handle GET request
        return render(request, 'input.html')

def get_coordinates(port, country):
    # Replace 'YOUR_API_KEY' with your actual API key from OpenCage
    api_key = '8beb1e16624349c78907b383ea5998e5'
    
    # Construct the request URL
    url = f'https://api.opencagedata.com/geocode/v1/json?q={port},{country}&key={api_key}'
    
    # Send the request to the OpenCage Geocoding API
    response = requests.get(url)
    
    # Parse the response JSON
    if response.status_code == 200:
        data = response.json()
        if data['total_results'] > 0:
            # Extract latitude and longitude from the response
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            return latitude, longitude
        else:
            # Handle no results found
            print("No results found.")
    else:
        # Handle HTTP request error
        print("Error:", response.status_code)
    
    return None, None
