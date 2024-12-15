import pandas as pd
from collections import defaultdict
import heapq
import datetime
import json
import numpy as np


def time_to_seconds(timestr):
    """Convert HH:MM:SS to seconds from midnight."""
    h, m, s = map(int, timestr.split(":"))
    return h * 3600 + m * 60 + s


def find_route_with_required_arrival(origin, destination, required_arrival_time_str):
    required_arrival_time = time_to_seconds(required_arrival_time_str)

    # Load preprocessed data
    stops = pd.read_csv("GTFS_Simplified/stops.txt", dtype={"stop_id": str})
    stop_times = pd.read_csv(
        "GTFS_Simplified/stop_times.txt", dtype={"trip_id": str, "stop_id": str}
    )
    connections = pd.read_csv("djkstra-gpt/connections.csv")
    with open("djkstra-gpt/arrivals_index.json", "r") as f:
        arrivals_index_data = json.load(f)

    # Convert arrivals_index_data to the required structure
    arrivals_index = defaultdict(list)
    for k, v in arrivals_index_data.items():
        # v is a list of [fstop, fdep, tarr, trip_id]
        arrivals_index[k] = v

    # Ensure shape_dist_traveled
    if "shape_dist_traveled" not in stop_times.columns:
        raise ValueError(
            "The stop_times.txt file must have a 'shape_dist_traveled' column."
        )

    # Create a lookup for shape_dist_traveled
    lookup_df = stop_times.set_index([stop_times.trip_id, stop_times.stop_id])

    # latest_arrival[stop]
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
        print(
            "No route found that arrives at {} by {}".format(
                destination, required_arrival_time_str
            )
        )
        return None, None, None

    # Reconstruct route forward
    route = [origin]
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
        route.append(next_stop)
        current = next_stop

    # Convert times to strings & add stop details
    for seg in route_info:
        if seg["arrival_sec"] is not None and seg["arrival_sec"] >= 0:
            seg["arrival_time_str"] = str(
                datetime.timedelta(seconds=int(seg["arrival_sec"]))
            )
        else:
            seg["arrival_time_str"] = "N/A"
        if seg["departure_sec"] is not None and seg["departure_sec"] >= 0:
            seg["departure_time_str"] = str(
                datetime.timedelta(seconds=int(seg["departure_sec"]))
            )
        else:
            seg["departure_time_str"] = "N/A"

        stop_row = stops[stops.stop_id == seg["stop_id"]]
        if not stop_row.empty:
            seg["stop_name"] = stop_row.iloc[0]["stop_name"]
            seg["stop_lat"] = stop_row.iloc[0]["stop_lat"]
            seg["stop_lon"] = stop_row.iloc[0]["stop_lon"]
        else:
            seg["stop_name"] = seg["stop_id"]
            seg["stop_lat"] = None
            seg["stop_lon"] = None

    print(
        "Found a route arriving by {} at {}:".format(
            required_arrival_time_str, route[-1]
        )
    )

    # Detect changes and waiting times
    route_rows = []
    for i, seg in enumerate(route_info):
        row = {
            "stop_id": seg["stop_id"],
            "stop_name": seg["stop_name"],
            "arrival_time": seg["arrival_time_str"],
            "departure_time": seg["departure_time_str"],
            "trip_id": seg["trip_id"],
            "change_notice": "",
        }

        if (
            i > 0
            and seg["trip_id"] != route_info[i - 1]["trip_id"]
            and seg["trip_id"] is not None
            and route_info[i - 1]["trip_id"] is not None
        ):
            prev_seg = route_info[i - 1]
            if (
                prev_seg["departure_sec"] is not None
                and prev_seg["arrival_sec"] is not None
            ):
                waiting_time_min = (
                    prev_seg["departure_sec"] - prev_seg["arrival_sec"]
                ) / 60.0
                row["change_notice"] = (
                    "Change here! Wait {:.1f} minutes for the next trip.".format(
                        waiting_time_min
                    )
                )
            else:
                row["change_notice"] = "Change here! (Waiting time unavailable)"
        route_rows.append(row)

    route_df = pd.DataFrame(route_rows)
    print(
        route_df[
            [
                "stop_id",
                "stop_name",
                "arrival_time",
                "departure_time",
                "trip_id",
                "change_notice",
            ]
        ]
    )

    # Distance & Time DataFrame
    dist_rows = []
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

        travel_time_min = travel_time_sec / 60.0
        if travel_time_sec > 0:
            avg_speed_kmh = (segment_distance_m * 3.6) / travel_time_sec
        else:
            avg_speed_kmh = 0

        dist_rows.append(
            {
                "from_stop_id": fstop,
                "from_stop_name": fseg["stop_name"],
                "to_stop_id": tstop,
                "to_stop_name": tseg["stop_name"],
                "distance_m": round(segment_distance_m, 2),
                "travel_time_min": travel_time_min,
                "average_speed_kmh": round(avg_speed_kmh),
            }
        )

    dist_df = pd.DataFrame(dist_rows)
    print("\nDistance & Time DataFrame:")
    print(dist_df)

    return route, route_df, dist_df


def build_od_tuples(filepath) -> list[tuple[str, str]]:
    file = pd.read_csv(filepath)
    return [tuple(row) for row in file["ao_stop_id", "wo_stop_id"].to_numpy()]


# =========================
# Example Usage:
# Just set these parameters and run the script.
# =========================
if __name__ == "__main__":
    required_arrivel_times = ["07:20:00", "07:30:00", "07:40:00", "07:50:00"]
    origin_destination_tuples = build_od_tuples("pendler/aggregate_pendler.csv")
    origin = "at:43:3162"
    destination = "at:49:1091"
    required_arrival_time_str = "08:50:00"

    route, route_df, dist_df = find_route_with_required_arrival(
        origin, destination, required_arrival_time_str
    )
    route_df.to_csv("djkstra-gpt/GPT_route.csv")
    dist_df.to_csv("djkstra-gpt/GPT_dist.csv")
