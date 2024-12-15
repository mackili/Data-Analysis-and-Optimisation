import json
import pandas as pd


# Function to parse NeTEx JSON file and extract required information
def parse_netex_file(netex_file):
    data = []

    with open(netex_file, "r") as file:
        netex_data = json.load(file)

    stop_places = netex_data["PublicationDelivery"]["dataObjects"]["CompositeFrame"][
        "frames"
    ]["SiteFrame"]["stopPlaces"]["StopPlace"]

    for stop_place in stop_places:
        station_id = str.replace(stop_place["@id"], "-", ":")
        wifi = stop_place.get("wirelessLAN")
        park_and_ride = (
            stop_place.get("Parking", {}).get("ParkingType") == "parkAndRide"
        )
        bike_and_ride = (
            stop_place.get("Parking", {}).get("ParkingType") == "bikeAndRide"
        )
        clocks = stop_place.get("clocks")
        passenger_info = stop_place.get("PassengerInformationEquipment", {}).get(
            "AccessibilityInfoFacilityList"
        )
        assistance_facilities = stop_place.get("AssistanceFacilityList")
        assistance_availability = stop_place.get("AssistanceAvailability")
        trained_staff = stop_place.get("AccessibilityTrainedStaff")
        rail_and_drive = stop_place.get("RailAndDrive")

        data.append(
            {
                "Station ID": station_id if station_id is not None else None,
                "WiFi": wifi if wifi is not None else "false",
                "Park and Ride": "Yes" if park_and_ride else "No",
                "Bike and Ride": "Yes" if bike_and_ride else "No",
                "Number of Clocks": clocks if clocks is not None else "0",
                "Passenger Info Available": (
                    "Yes" if passenger_info is not None else "No"
                ),
                "Assistance Facilities": (
                    assistance_facilities if assistance_facilities is not None else "No"
                ),
                "Assistance Availability": (
                    assistance_availability
                    if assistance_availability is not None
                    else "No"
                ),
                "Trained Staff": "Yes" if trained_staff is not None else "No",
                "Rail and Drive": "Yes" if rail_and_drive is not None else "No",
            }
        )

    return pd.DataFrame(data)


# Function to filter NeTEx data based on GTFS station IDs
def filter_by_gtfs(netex_data, gtfs_file):
    gtfs_stations = pd.read_csv(gtfs_file)
    gtfs_station_ids = set(gtfs_stations["stop_id"])  # Adjust column name if different

    # Filter NeTEx data
    filtered_data = netex_data[netex_data["Station ID"].isin(gtfs_station_ids)]
    return netex_data


# Main function
def main(netex_file, gtfs_file, output_file):
    print("Parsing NeTEx file...")
    netex_data = parse_netex_file(netex_file)

    print("Filtering data by GTFS stations...")
    filtered_data = filter_by_gtfs(netex_data, gtfs_file)

    print("Saving filtered data to CSV...")
    filtered_data.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")


# Example usage
# Replace 'netex.xml' and 'gtfs_stations.csv' with actual file paths
if __name__ == "__main__":
    netex_file = "NetEx/netex_oebb_StoppPlaces.json"
    gtfs_file = "GTFS_Simplified/stops.txt"
    output_file = "NetEx/station-amenities.csv"
    main(netex_file, gtfs_file, output_file)
