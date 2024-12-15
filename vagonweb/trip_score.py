import json
import pandas as pd
from collections import Counter
from tqdm import tqdm

path = "vagonweb/webscraping_result.json"
netex_path = "GTFS_Simplified/trips.txt"


def computeStatistics(data) -> None:
    # Count empty lists
    empty_count = sum(1 for v in data.values() if not v)

    # Count occurrences of concatenated contents
    concatenated_counter = Counter()
    for v in data.values():
        concatenated_content = ":".join(v)
        concatenated_counter.update([concatenated_content])

    # Print statistics
    print(f"Total number of trips: {len(data)}")
    print(f"Number of empty lists: {empty_count}")
    print("Concatenated content occurrences:")
    for content, count in concatenated_counter.items():
        print(f"{content}: {count}")


def findGTFS() -> pd.DataFrame:
    trips = pd.read_csv(netex_path)
    trips["trip_short_name"] = trips["trip_short_name"].str.extract("(\d+)")
    return trips[["trip_short_name", "trip_id", "route_id"]]


def computeAttributes(data: dict) -> pd.DataFrame:
    attribute_list = []
    fahrzeuge = pd.read_csv("vagonweb/OBB Baureihen.csv")
    gtfs = findGTFS()
    for trip in tqdm(data, desc="Processing trips"):
        composition = data.get(trip)
        gtfs_trip_id = (
            gtfs[gtfs["trip_short_name"] == trip]["trip_id"].values[0]
            if not gtfs[gtfs["trip_short_name"] == trip].empty
            else None
        )
        gtfs_route_id = (
            gtfs[gtfs["trip_short_name"] == trip]["route_id"].values[0]
            if not gtfs[gtfs["trip_short_name"] == trip].empty
            else None
        )
        attr = {
            "trip": trip,
            "gtfs-trip-id": gtfs_trip_id,
            "gtfs-route-id": gtfs_route_id,
        }
        for carriage in composition:
            attributes = fahrzeuge[fahrzeuge["Number"].isin([carriage])]
            if len(attributes) < 1:
                continue
            attr = {
                "trip": trip,
                "gtfs-trip-id": gtfs_trip_id,
                "gtfs-route-id": gtfs_route_id,
                "cctv": False if not ("cctv" in attr.keys()) else attr["cctv"],
                "Wheelchair": (
                    False if not ("Wheelchair" in attr.keys()) else attr["cctv"]
                ),
                "Bicycle": False if not ("Bicycle" in attr.keys()) else attr["Bicycle"],
                "ac": False if not ("ac" in attr.keys()) else attr["ac"],
                "WiFi": False if not ("WiFi" in attr.keys()) else attr["WiFi"],
                "LowFloor": (
                    False if not ("LowFloor" in attr.keys()) else attr["LowFloor"]
                ),
                "Year": int,
            }
            attr["ac"] = (
                True
                if attributes["Klimatisierter Fahrgastinnenraum"].values[0] == "ja"
                or attr["ac"]
                else False
            )
            attr["Bicycle"] = (
                True
                if attributes["Fahrradplätze"].values[0] == "ja" or attr["Bicycle"]
                else False
            )
            attr["cctv"] = (
                True
                if attributes["Videoüberwachung"].values[0] == "ja" or attr["cctv"]
                else False
            )
            attr["LowFloor"] = (
                True
                if attributes["Niederflurzustieg"].values[0] == "ja" or attr["LowFloor"]
                else False
            )
            attr["Wheelchair"] = (
                True
                if not (attributes["Rollstuhlplätze"].values[0] == "-")
                or attr["Wheelchair"]
                else False
            )
            attr["WiFi"] = (
                True if attributes["W-LAN"].values[0] == "ja" or attr["WiFi"] else False
            )

        attribute_list.append(attr)
    return pd.DataFrame(attribute_list)


def main():
    with open(path, "r") as file:
        data = json.load(file)
    # computeStatistics(data)
    computeAttributes(data).to_csv("vagonweb/trip_attributes.csv")


if __name__ == "__main__":
    main()
