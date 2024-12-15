import pandas as pd
from collections import defaultdict
import heapq
import datetime
import json
import os
import numpy as np
from tqdm import tqdm


def time_to_seconds(timestr):
    """Convert HH:MM:SS to seconds from midnight."""
    h, m, s = map(int, timestr.split(":"))
    return h * 3600 + m * 60 + s


def find_route_with_required_arrival(
    origin,
    destination,
    required_arrival_time_str,
    stops,
    stop_times,
    connections,
    arrivals_index,
):
    required_arrival_time = time_to_seconds(required_arrival_time_str)

    if "shape_dist_traveled" not in stop_times.columns:
        raise ValueError(
            "The stop_times.txt file must have a 'shape_dist_traveled' column."
        )

    lookup_df = stop_times.set_index([stop_times.trip_id, stop_times.stop_id])

    latest_arrival = defaultdict(lambda: -1)
    latest_arrival[destination] = required_arrival_time

    pq = [(-required_arrival_time, destination)]
    predecessor = {}

    # Backward search
    while pq:
        cur_neg_time, cur_stop = heapq.heappop(pq)
        cur_time = -cur_neg_time

        if cur_time < latest_arrival[cur_stop]:
            continue

        if cur_stop in arrivals_index:
            for fstop, fdep, tarr, trip_id in arrivals_index[cur_stop]:
                if cur_time >= tarr:
                    if fdep > latest_arrival[fstop]:
                        latest_arrival[fstop] = fdep
                        predecessor[fstop] = (cur_stop, fdep, tarr, trip_id)
                        heapq.heappush(pq, (-fdep, fstop))

    if latest_arrival[origin] == -1:
        # No route found
        return None, None

    # Reconstruct route forward
    route_info = [
        {
            "stop_id": origin,
            "arrival_sec": latest_arrival[origin],
            "departure_sec": None,
            "trip_id": None,
        }
    ]

    current = origin
    while current in predecessor:
        next_stop, fdep, tarr, trip_id = predecessor[current]
        route_info[-1]["departure_sec"] = fdep
        route_info[-1]["trip_id"] = trip_id
        route_info.append(
            {
                "stop_id": next_stop,
                "arrival_sec": tarr,
                "departure_sec": None,
                "trip_id": trip_id,
            }
        )
        current = next_stop

    # Convert times and gather stop info
    for seg in route_info:
        seg["arrival_time_str"] = (
            str(datetime.timedelta(seconds=int(seg["arrival_sec"])))
            if seg["arrival_sec"] is not None and seg["arrival_sec"] >= 0
            else "N/A"
        )
        seg["departure_time_str"] = (
            str(datetime.timedelta(seconds=int(seg["departure_sec"])))
            if seg["departure_sec"] is not None and seg["departure_sec"] >= 0
            else "N/A"
        )

        stop_row = stops[stops.stop_id == seg["stop_id"]]
        seg["stop_name"] = (
            stop_row.iloc[0]["stop_name"] if not stop_row.empty else seg["stop_id"]
        )

    # Changes
    changes = []
    change_count = 0
    origin_dep_sec = (
        route_info[0]["departure_sec"]
        if route_info[0]["departure_sec"] is not None
        else route_info[0]["arrival_sec"]
    )
    final_arr_sec = route_info[-1]["arrival_sec"]

    for i in range(len(route_info)):
        if (
            i > 0
            and route_info[i]["trip_id"] != route_info[i - 1]["trip_id"]
            and route_info[i]["trip_id"] is not None
            and route_info[i - 1]["trip_id"] is not None
        ):
            curr_seg = route_info[i]
            if (
                curr_seg["departure_sec"] is not None
                and curr_seg["arrival_sec"] is not None
            ):
                waiting_time_sec = curr_seg["departure_sec"] - curr_seg["arrival_sec"]
                changes.append(
                    {
                        "station": curr_seg["stop_name"],
                        "duration": int(waiting_time_sec) / 60,
                        "sequence": i,
                    }
                )
                change_count += 1

    # Trip segments
    trip_segments = defaultdict(list)
    for i in range(len(route_info) - 1):
        fseg = route_info[i]
        tseg = route_info[i + 1]
        trip_id = fseg["trip_id"]
        if trip_id is None:
            continue
        fstop = fseg["stop_id"]
        tstop = tseg["stop_id"]
        try:
            f_dist = float(lookup_df.loc[(trip_id, fstop), "shape_dist_traveled"])
            t_dist = float(lookup_df.loc[(trip_id, tstop), "shape_dist_traveled"])
        except KeyError:
            continue

        segment_distance_m = t_dist - f_dist
        if fseg["departure_sec"] is not None and tseg["arrival_sec"] is not None:
            travel_time_sec = tseg["arrival_sec"] - fseg["departure_sec"]
        else:
            continue

        avg_speed_kmh = (
            (segment_distance_m * 3.6) / travel_time_sec if travel_time_sec > 0 else 0
        )

        trip_segments[trip_id].append(
            {
                "from": fseg["stop_name"],
                "departure": fseg["departure_time_str"],
                "to": tseg["stop_name"],
                "arrival": tseg["arrival_time_str"],
                "duration": int(travel_time_sec),
                "distance": int(segment_distance_m),
                "speed": avg_speed_kmh,
            }
        )

    # Build trips_info
    trips_info = {}
    for trip_id, segments in trip_segments.items():
        total_duration = sum(s["duration"] for s in segments)
        total_distance = sum(s["distance"] for s in segments)
        stop_count = len(segments) + 1
        avg_speed_kmh = (
            (total_distance * 3.6 / total_duration) if total_duration > 0 else 0
        )

        trips_info[trip_id] = {
            "from": segments[0]["from"],
            "to": segments[-1]["to"],
            "duration": total_duration,
            "stop_count": stop_count,
            "average_speed": avg_speed_kmh,
            "via": segments,
        }

    total_duration = (
        final_arr_sec - origin_dep_sec
        if (final_arr_sec is not None and origin_dep_sec is not None)
        else 0
    )
    key = f"{origin}-{destination}-{required_arrival_time_str}"
    result = {
        "from": origin,
        "departure": route_info[0]["departure_time_str"],
        "to": destination,
        "arrival": route_info[-1]["arrival_time_str"],
        "trips": trips_info,
        "duration": total_duration,
        "changeCount": change_count,
        "changesAt": changes,
    }

    return key, result


if __name__ == "__main__":
    # Load preprocessed data
    stops = pd.read_csv("GTFS_Simplified/stops.txt", dtype={"stop_id": str})
    stop_times = pd.read_csv(
        "GTFS_Simplified/stop_times.txt", dtype={"trip_id": str, "stop_id": str}
    )
    connections = pd.read_csv("djkstra-gpt/connections.csv")
    with open("djkstra-gpt/arrivals_index.json", "r") as f:
        arrivals_index_data = json.load(f)

    arrivals_index = defaultdict(list)
    for k, v in arrivals_index_data.items():
        arrivals_index[k] = v

    # Example: run for multiple (origin, destination) pairs and multiple arrival times
    df = pd.read_csv("pendler/aggregate_pendler.csv")
    origins_destinations = [
        tuple(row) for row in df[["ao_stop_id", "wo_stop_id"]].to_numpy()
    ]

    arrival_times = ["07:20:00", "07:30:00", "07:40:00", "07:50:00"]

    all_results = {}

    for origin, destination in tqdm(
        origins_destinations, desc="Processing origin-destination pairs"
    ):
        for arr_time in arrival_times:
            key, res = find_route_with_required_arrival(
                origin,
                destination,
                arr_time,
                stops,
                stop_times,
                connections,
                arrivals_index,
            )
            if res is not None:
                all_results[key] = res
            else:
                # If no route found, we can also store a placeholder or skip
                all_results[key] = {"error": "No route found"}

    # Save all results to a JSON file
    with open("djkstra-gpt/results.json", "w") as f:
        json.dump(all_results, f, indent=2)
