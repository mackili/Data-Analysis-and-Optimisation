import xml.etree.ElementTree as ET
import json
from geojson import Point, Feature, FeatureCollection, LineString

# Define file paths as string variables
stations_input_path = "NetEx/ÖBB NetEx files/netex_oebb_StoppPlaces_20231211.xml"  # Replace with the actual path to your stations XML file
network_input_path = "NetEx/ÖBB NetEx files/netex_oebb_InfrastructureNetwork_20231211.xml"  # Replace with the actual path to your network XML file
stops_output_path = "NetEx/ÖBB NetEx files/haltestellen.geojson"
network_output_path = "NetEx/ÖBB NetEx files/network.geojson"


def parse_stations_to_geojson(stations_input_path, stops_output_path):
    # Load the Stations XML from the specified input file
    with open(stations_input_path, "r", encoding="utf-8") as file:
        stations_xml = file.read()

    # Parse the XML
    root = ET.fromstring(stations_xml)

    # Extract Haltestellen (Stops)
    stops = []
    for stop in root.findall(".//{http://www.netex.org.uk/netex}StopPlace"):
        name = stop.find("{http://www.netex.org.uk/netex}Name").text
        description = stop.find("{http://www.netex.org.uk/netex}Description")
        description_text = description.text if description is not None else ""
        longitude = float(stop.find(".//{http://www.netex.org.uk/netex}Longitude").text)
        latitude = float(stop.find(".//{http://www.netex.org.uk/netex}Latitude").text)

        # Extract additional attributes from keyList if present
        key_values = {}
        for key_value in stop.findall(".//{http://www.netex.org.uk/netex}KeyValue"):
            key = key_value.find("{http://www.netex.org.uk/netex}Key").text
            value = key_value.find("{http://www.netex.org.uk/netex}Value").text
            key_values[key] = value

        # Add stop as GeoJSON feature with all attributes
        point = Point((longitude, latitude))
        feature = Feature(
            geometry=point,
            properties={
                "name": name,
                "description": description_text,
                "key_values": key_values,
            },
        )
        stops.append(feature)

    # Create GeoJSON FeatureCollection for stops
    stops_geojson = FeatureCollection(stops)

    # Save to GeoJSON file (creates file if it doesn't exist)
    with open(stops_output_path, "w", encoding="utf-8") as f:
        json.dump(stops_geojson, f, indent=2)
    print("GeoJSON file created for stations:", stops_output_path)


def parse_network_to_geojson(network_input_path, network_output_path):
    # Load the Network XML from the specified input file
    with open(network_input_path, "r", encoding="utf-8") as file:
        network_xml = file.read()

    # Parse the XML
    root = ET.fromstring(network_xml)

    # Extract Streckennetz (Network)
    network_elements = []
    for element in root.findall(".//{http://www.netex.org.uk/netex}RailwayElement"):
        name = element.find("{http://www.netex.org.uk/netex}Name").text
        pos_list = (
            element.find(".//{http://www.opengis.net/gml/3.2}posList")
            .text.strip()
            .split()
        )

        # Convert coordinates to tuples
        coordinates = [
            (float(pos_list[i]), float(pos_list[i + 1]))
            for i in range(0, len(pos_list), 2)
        ]

        # Add network element as GeoJSON feature
        line = LineString(coordinates)
        feature = Feature(
            geometry=line,
            properties={
                "name": name
                # Add other attributes as needed
            },
        )
        network_elements.append(feature)

    # Create GeoJSON FeatureCollection for network
    network_geojson = FeatureCollection(network_elements)

    # Save to GeoJSON file (creates file if it doesn't exist)
    with open(network_output_path, "w", encoding="utf-8") as f:
        json.dump(network_geojson, f, indent=2)
    print("GeoJSON file created for network:", network_output_path)


def parse_network_to_geojson2(network_input_path, network_output_path):
    # Load the Infrastructure XML from the specified input file
    with open(network_input_path, "r", encoding="utf-8") as file:
        network_xml = file.read()

    # Parse the XML
    root = ET.fromstring(network_xml)

    # Initialize lists to hold GeoJSON features
    railway_junctions = []
    railway_elements = []

    # Extract `RailwayJunction` elements
    for junction in root.findall(".//{http://www.netex.org.uk/netex}RailwayJunction"):
        name = junction.find("{http://www.netex.org.uk/netex}Name").text
        longitude = float(
            junction.find(".//{http://www.netex.org.uk/netex}Longitude").text
        )
        latitude = float(
            junction.find(".//{http://www.netex.org.uk/netex}Latitude").text
        )
        junction_id = junction.get("id")
        version = junction.get("version")

        # Create GeoJSON point feature
        point = Point((longitude, latitude))
        feature = Feature(
            geometry=point,
            properties={"id": junction_id, "version": version, "name": name},
        )
        railway_junctions.append(feature)

    # Extract `RailwayElement` elements
    for element in root.findall(".//{http://www.netex.org.uk/netex}RailwayElement"):
        element_id = element.get("id")
        version = element.get("version")
        name = (
            element.find("{http://www.netex.org.uk/netex}Name").text
            if element.find("{http://www.netex.org.uk/netex}Name") is not None
            else None
        )
        from_point_ref = element.find(
            "{http://www.netex.org.uk/netex}FromPointRef"
        ).get("ref")
        to_point_ref = element.find("{http://www.netex.org.uk/netex}ToPointRef").get(
            "ref"
        )

        # Parse the coordinates in `gml:posList`
        pos_list = (
            element.find(".//{http://www.opengis.net/gml/3.2}posList")
            .text.strip()
            .split()
        )
        coordinates = [
            (float(pos_list[i]), float(pos_list[i + 1]))
            for i in range(0, len(pos_list), 2)
        ]

        # Create GeoJSON LineString feature
        line = LineString(coordinates)
        feature = Feature(
            geometry=line,
            properties={
                "id": element_id,
                "version": version,
                "name": name,
                "from_point_ref": from_point_ref,
                "to_point_ref": to_point_ref,
            },
        )
        railway_elements.append(feature)

    # Create GeoJSON FeatureCollections
    junctions_geojson = FeatureCollection(railway_junctions)
    elements_geojson = FeatureCollection(railway_elements)

    # Save each to GeoJSON file
    with open(
        network_output_path.replace("network.geojson", "junctions.geojson"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(junctions_geojson, f, indent=2)

    with open(network_output_path, "w", encoding="utf-8") as f:
        json.dump(elements_geojson, f, indent=2)

    print("GeoJSON files created for railway junctions and elements.")


# Usage
parse_stations_to_geojson(stations_input_path, stops_output_path)
parse_network_to_geojson2(network_input_path, network_output_path)
