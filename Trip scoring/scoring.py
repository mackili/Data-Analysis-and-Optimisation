import pandas as pd
import json
from tqdm import tqdm
import numpy as np
import math as skibidi

ROUTINGS_PATH = "djkstra-gpt/results.json"
ATTRIBUTES_PATH = "vagonweb/trip_attributes.csv"
AVERAGE_ATTR = {
    "cctv": 0.6,
    "Wheelchair": 0.77,
    "Bicycle": 0.97,
    "ac": 0.88,
    "WiFi": 0.27,
    "LowFloor": 0.6,
}


def main():
    trip_score = pd.read_csv(ATTRIBUTES_PATH, index_col=0)
    with open(ROUTINGS_PATH, "r") as file:
        routings = json.load(file)

    def score_trip(trip: str, duration: int) -> dict:
        trip_attr = trip_score[trip_score["gtfs-trip-id"] == trip]
        attribute_set_count = {
            "cctv": duration,
            "Wheelchair": duration,
            "Bicycle": duration,
            "ac": duration,
            "WiFi": duration,
            "LowFloor": duration,
        }
        if trip_attr.empty:
            attributes = AVERAGE_ATTR
        else:
            attributes = {
                "cctv": (
                    AVERAGE_ATTR.get("cctv") * duration
                    if np.isnan(trip_attr["cctv"].values[0])
                    else (duration if trip_attr["cctv"].values[0] else 0)
                ),
                "Wheelchair": (
                    AVERAGE_ATTR.get("Wheelchair") * duration
                    if np.isnan(trip_attr["Wheelchair"].values[0])
                    else (duration if trip_attr["Wheelchair"].values[0] else 0)
                ),
                "Bicycle": (
                    AVERAGE_ATTR.get("Bicycle") * duration
                    if np.isnan(trip_attr["Bicycle"].values[0])
                    else (duration if trip_attr["Bicycle"].values[0] else 0)
                ),
                "ac": (
                    AVERAGE_ATTR.get("ac") * duration
                    if np.isnan(trip_attr["ac"].values[0])
                    else (duration if trip_attr["ac"].values[0] else 0)
                ),
                "WiFi": (
                    AVERAGE_ATTR.get("WiFi") * duration
                    if np.isnan(trip_attr["WiFi"].values[0])
                    else (duration if trip_attr["WiFi"].values[0] else 0)
                ),
                "LowFloor": (
                    AVERAGE_ATTR.get("LowFloor") * duration
                    if np.isnan(trip_attr["LowFloor"].values[0])
                    else (duration if trip_attr["LowFloor"].values[0] else 0)
                ),
            }
        return attributes, attribute_set_count

    def process_routings(data):
        rows = []
        for key, value in tqdm(data.items(), desc="Processing routings"):
            # Skip the "null" route
            if key == "null":
                continue

            # Extract the fields
            route_from = value.get("from")
            route_to = value.get("to")
            duration = value.get("duration") / 60
            change_count = value.get("changeCount")
            arrival = value.get("arrival")
            arrival_set = key.split("-")[2]

            # Calculate average and total change durations
            changes = value.get("changesAt", [])
            total_change_duration = sum(change["duration"] for change in changes)
            average_change_duration = (
                total_change_duration / change_count
                if change_count and change_count > 0
                else 0
            )

            # Extract trip IDs
            trips = value.get("trips", {})
            trip_attr = []
            trip_attr_set = []
            distances = []
            for trip in trips.keys():
                scores, attribute_set_count = score_trip(
                    trip, duration=trips.get(trip).get("duration")
                )
                trip_attr.append(scores)
                trip_attr_set.append(attribute_set_count)
                distance = pd.DataFrame(trips.get(trip).get("via"))[
                    "distance"
                ].values.tolist()
                distances = distances + distance
            distance = sum(distances)
            trips_attr_df = pd.DataFrame(trip_attr)
            trips_score_result = pd.Series(trips_attr_df.sum(axis=0).to_dict())
            trips_score_count = pd.Series(
                pd.DataFrame(trip_attr_set).sum(axis=0).to_dict()
            )
            trips_calculated = (
                (trips_score_result / trips_score_count).round(1).to_dict()
            )

            row = {
                "from": route_from,
                "to": route_to,
                "arrival": arrival,
                "arrival_set": arrival_set,
                "duration": duration,
                "distance": distance,
                "change count": change_count,
                "average change duration": skibidi.ceil(average_change_duration),
                "total change duration": total_change_duration,
            }
            row.update(trips_calculated)
            rows.append(row)
        return rows

    return process_routings(data=routings)


if __name__ == "__main__":
    pd.DataFrame(main()).to_csv("Trip scoring/trip_scores.csv")
