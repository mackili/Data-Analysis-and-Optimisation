import pandas as pd
from collections import defaultdict
import heapq
import datetime


def time_to_seconds(timestr):
    """Convert HH:MM:SS to seconds from midnight."""
    h, m, s = map(int, timestr.split(":"))
    return h * 3600 + m * 60 + s


# =========================
# Step 1: Read GTFS Data
# =========================
stops = pd.read_csv("GTFS_Simplified/stops.txt", dtype={"stop_id": str})
stop_times = pd.read_csv(
    "GTFS_Simplified/stop_times.txt", dtype={"trip_id": str, "stop_id": str}
)

# Ensure we have shape_dist_traveled
if "shape_dist_traveled" not in stop_times.columns:
    raise ValueError(
        "The stop_times.txt file must have a 'shape_dist_traveled' column."
    )

# Convert times to seconds
stop_times["arrival_sec"] = stop_times["arrival_time"].apply(time_to_seconds)
stop_times["departure_sec"] = stop_times["departure_time"].apply(time_to_seconds)

# Sort by trip_id and stop_sequence to ensure proper order
stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])

# Create a quick index for lookups: (trip_id, stop_id) → shape_dist, arrival_sec, departure_sec
trip_stop_key = list(zip(stop_times.trip_id, stop_times.stop_id))
lookup_df = stop_times.set_index([stop_times.trip_id, stop_times.stop_id])

# =========================
# Step 2: Build Connections
# Each connection: (fstop, fdep, tstop, tarr, trip_id)
# =========================
connections = []
trip_ids = stop_times["trip_id"].unique()

for trip in trip_ids:
    trip_df = stop_times[stop_times.trip_id == trip].sort_values("stop_sequence")
    for i in range(len(trip_df) - 1):
        f = trip_df.iloc[i]
        t = trip_df.iloc[i + 1]
        connections.append(
            (f["stop_id"], f["departure_sec"], t["stop_id"], t["arrival_sec"], trip)
        )

# =========================
# Step 3: Index Connections by Arrival Stop for Backward Search
# =========================
arrivals_index = defaultdict(list)
for fstop, fdep, tstop, tarr, trip_id in connections:
    arrivals_index[tstop].append((fstop, fdep, tarr, trip_id))


# =========================
# Step 4: Backward Search Algorithm
# =========================
def find_route_with_required_arrival(origin, destination, required_arrival_time_str):
    required_arrival_time = time_to_seconds(required_arrival_time_str)

    # latest_arrival[stop] = latest time we can be at `stop` and still reach `destination` by required time
    latest_arrival = defaultdict(lambda: -1)
    latest_arrival[destination] = required_arrival_time

    # Priority queue (max-heap by time)
    pq = [(-required_arrival_time, destination)]

    # predecessor[stop] = (next_stop, fdep, tarr, trip_id)
    predecessor = {}

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

    # =========================
    # Step 5: Reconstruct the Route Forward
    # =========================
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
        # Update departure time and trip_id for current segment
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

    # Convert times to strings and add stop info
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

        # Merge with stops info
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

        # Check if there's a trip change at this stop
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

    # =========================
    # Step 6: Create a Distance & Time DataFrame
    # For each segment (from route_info[i] to route_info[i+1]):
    # We'll find the distance from shape_dist_traveled, compute travel time in minutes, and average speed.
    # =========================
    dist_rows = []
    for i in range(len(route_info) - 1):
        fseg = route_info[i]
        tseg = route_info[i + 1]
        # Both should be on the same trip if continuous journey, but might have changes.
        # We'll use the trip_id of the segment from fstop to tstop.
        trip_id = fseg["trip_id"]
        if trip_id is None:
            # If we have a segment without trip_id, skip
            continue

        fstop = fseg["stop_id"]
        tstop = tseg["stop_id"]

        # Lookup shape_dist_traveled for both stops on the given trip
        try:
            f_dist = float(lookup_df.loc[(trip_id, fstop), "shape_dist_traveled"])
            t_dist = float(lookup_df.loc[(trip_id, tstop), "shape_dist_traveled"])
        except KeyError:
            # If for some reason the data isn't found, skip this segment
            continue

        segment_distance_m = t_dist - f_dist

        # Compute travel time
        if fseg["departure_sec"] is not None and tseg["arrival_sec"] is not None:
            travel_time_sec = tseg["arrival_sec"] - fseg["departure_sec"]
        else:
            # If times aren't available, skip
            continue

        travel_time_min = travel_time_sec / 60.0
        # Average speed in km/h
        # distance (m) -> km, time (min) -> hr, so speed = (distance_m / 1000) / (travel_time_min / 60)
        # = (distance_m * 60) / (1000 * travel_time_min)
        if travel_time_min > 0:
            avg_speed_kmh = (segment_distance_m * 3.6) / (travel_time_sec)
        else:
            avg_speed_kmh = 0

        dist_rows.append(
            {
                "from_stop_id": fstop,
                "from_stop_name": fseg["stop_name"],
                "to_stop_id": tstop,
                "to_stop_name": tseg["stop_name"],
                "distance_m": segment_distance_m,
                "travel_time_min": travel_time_min,
                "average_speed_kmh": avg_speed_kmh,
            }
        )

    dist_df = pd.DataFrame(dist_rows)
    print("\nDistance & Time DataFrame:")
    print(dist_df)

    return route, route_df, dist_df


# =========================
# Example Usage:
# =========================
origin = "at:43:3162"  # Your origin stop_id
destination = "at:43:7105"  # Your destination stop_id
required_arrival_time_str = "13:30:00"  # Required arrival time

route, route_df, dist_df = find_route_with_required_arrival(
    origin, destination, required_arrival_time_str
)
