# %%
import csv
import json


# %%
def __read_stops__() -> dict:
    parent_stops = {}
    child_stops = []
    with open("GTFS_OP_2024_obb/stops.txt", "r") as stops:
        reader = csv.DictReader(stops)
        for row in reader:
            stop_id = row.pop("\ufeffstop_id")
            if stop_id.startswith("P") or row["parent_station"] == "":
                row["child_stops"] = []
                parent_stops[stop_id] = row
            else:
                row["\ufeffstop_id"] = stop_id
                child_stops.append(row)
        # add child stops to parents
        stops: dict = append_children_stops(parent_stops, child_stops)
    return parent_stops


def append_children_stops(parent_stops: dict, children_stops: list) -> dict:
    for stop in children_stops:
        parent_id = stop["parent_station"]
        parent = parent_stops.get(parent_id)
        parent["child_stops"].append(stop)
    return parent_stops


def __write_stops_to_json__(stops: dict, file_path: str):
    with open(file_path, "w") as json_file:
        json.dump(stops, json_file, indent=4)


def __write_stops_to_geojson__(stops: dict, file_path: str):
    geojson = {"type": "FeatureCollection", "features": []}

    for stop_id, stop_data in stops.items():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(stop_data["stop_lon"]),
                    float(stop_data["stop_lat"]),
                ],
            },
            "properties": {
                "stop_id": stop_id,
                "stop_name": stop_data["stop_name"],
                "stop_desc": stop_data.get("stop_desc", ""),
                "parent_station": stop_data.get("parent_station", ""),
                "child_stops": stop_data["child_stops"],
            },
        }
        geojson["features"].append(feature)

    with open(file_path, "w") as geojson_file:
        json.dump(geojson, geojson_file, indent=4)


stops = __read_stops__()
__write_stops_to_json__(stops, "GTFS JSON files/stops.json")
__write_stops_to_geojson__(stops, "GTFS JSON files/stops.geojson")
