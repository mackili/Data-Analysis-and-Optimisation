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

# Convert times to seconds
stop_times["arrival_sec"] = stop_times["arrival_time"].apply(time_to_seconds)
stop_times["departure_sec"] = stop_times["departure_time"].apply(time_to_seconds)

# Sort by trip_id and stop_sequence to ensure proper order
stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])

# =========================
# Step 2: Build Connections
# Each connection: (fstop, fdep, tstop, tarr, trip_id)
# This represents traveling from fstop departing at fdep (seconds)
# to tstop arriving at tarr (seconds) on a given trip_id.
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
# arrivals_index[tstop] gives a list of connections (fstop, fdep, tarr, trip_id)
# that can get you to tstop by tarr if you start at fstop by fdep.
# =========================
arrivals_index = defaultdict(list)
for fstop, fdep, tstop, tarr, trip_id in connections:
    arrivals_index[tstop].append((fstop, fdep, tarr, trip_id))


# =========================
# Step 4: Backward Search Algorithm
# Given a destination and required arrival time, find the latest feasible departure times.
# We'll track predecessor to reconstruct route and trips.
# =========================
def find_route_with_required_arrival(origin, destination, required_arrival_time_str):
    required_arrival_time = time_to_seconds(required_arrival_time_str)

    # latest_arrival[stop] = latest time we can be at `stop` and still reach `destination` by required time
    latest_arrival = defaultdict(lambda: -1)
    latest_arrival[destination] = required_arrival_time

    # Priority queue for backward search (max-heap by time, use negative because Python has min-heap)
    # Stored as (-time, stop)
    pq = [(-required_arrival_time, destination)]

    # predecessor[stop] = (next_stop, fdep, tarr, trip_id)
    # Means: from `stop` forward we go to `next_stop` arriving at `tarr`, departing from `stop` at `fdep` on `trip_id`.
    predecessor = {}

    while pq:
        cur_neg_time, cur_stop = heapq.heappop(pq)
        cur_time = -cur_neg_time

        # If this is not the best known time for this stop, skip
        if cur_time < latest_arrival[cur_stop]:
            continue

        # Explore incoming connections to cur_stop
        if cur_stop in arrivals_index:
            for fstop, fdep, tarr, trip_id in arrivals_index[cur_stop]:
                # To use this connection backward: we must arrive at cur_stop by cur_time
                # The connection arrives at cur_stop at tarr.
                # If cur_time >= tarr, we can be at fstop by fdep.
                if cur_time >= tarr:
                    if fdep > latest_arrival[fstop]:
                        latest_arrival[fstop] = fdep
                        predecessor[fstop] = (cur_stop, fdep, tarr, trip_id)
                        heapq.heappush(pq, (-fdep, fstop))

    # If no route found
    if latest_arrival[origin] == -1:
        print(
            "No route found that arrives at {} by {}".format(
                destination, required_arrival_time_str
            )
        )
        return None, None

    # =========================
    # Step 5: Reconstruct the Route Forward
    # We have predecessor information that tells us how to go from one stop to the next.
    # We'll start from origin and follow the chain to the destination.
    # =========================
    route = [origin]
    current = origin
    # We'll store detailed segment info: (stop, arrival_time, departure_time, trip_id)
    # For the origin, we only know we can be there by latest_arrival[origin]. The departure time
    # from origin will come from the first leg.
    route_info = []

    # The arrival time at the origin is latest_arrival[origin].
    # departure_time and trip_id will come once we know the next leg.
    origin_arr_time = latest_arrival[origin]
    route_info.append(
        {
            "stop_id": origin,
            "arrival_sec": origin_arr_time,
            "departure_sec": None,  # will fill when we see next leg
            "trip_id": None,
        }
    )

    while current in predecessor:
        next_stop, fdep, tarr, trip_id = predecessor[current]
        # The segment is current -> next_stop
        # We know we depart current at fdep and arrive next_stop at tarr on trip_id
        # Update departure time for current stop
        route_info[-1]["departure_sec"] = fdep
        route_info[-1]["trip_id"] = trip_id

        # Add next_stop info
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

    # Now we have a chain of stops with arrival/departure times and trips.

    # Convert times to human-readable and detect changes
    # A change occurs if trip_id changes between segments.
    # Also calculate waiting time at transfer stations.
    for seg in route_info:
        if seg["arrival_sec"] is not None:
            seg["arrival_time_str"] = str(
                datetime.timedelta(seconds=int(seg["arrival_sec"]))
            )
        else:
            seg["arrival_time_str"] = "N/A"
        if seg["departure_sec"] is not None:
            seg["departure_time_str"] = str(
                datetime.timedelta(seconds=int(seg["departure_sec"]))
            )
        else:
            seg["departure_time_str"] = "N/A"

        # Merge with stop info
        stop_row = stops[stops.stop_id == seg["stop_id"]]
        if not stop_row.empty:
            seg["stop_name"] = stop_row.iloc[0]["stop_name"]
            seg["stop_lat"] = stop_row.iloc[0]["stop_lat"]
            seg["stop_lon"] = stop_row.iloc[0]["stop_lon"]
        else:
            seg["stop_name"] = seg["stop_id"]
            seg["stop_lat"] = None
            seg["stop_lon"] = None

    # Print route details
    print(
        "Found a route arriving by {} at {}:".format(
            required_arrival_time_str, route[-1]
        )
    )
    route_rows = []
    for i, seg in enumerate(route_info):
        row = {
            "stop_id": seg["stop_id"],
            "stop_name": seg["stop_name"],
            "arrival_time": seg["arrival_time_str"],
            "departure_time": seg["departure_time_str"],
            "trip_id": seg["trip_id"],
        }

        # Check if there's a trip change at this stop (except the last stop which doesn't depart)
        if (
            i > 0
            and seg["trip_id"] != route_info[i - 1]["trip_id"]
            and seg["trip_id"] is not None
            and route_info[i - 1]["trip_id"] is not None
        ):
            # Trip changed
            # Waiting time = departure_sec(current) - arrival_sec(previous)
            # Actually, the change is noticed at the previous segment's stop
            prev_seg = route_info[i - 1]
            if (
                prev_seg["departure_sec"] is not None
                and prev_seg["arrival_sec"] is not None
            ):
                # If we consider waiting: we arrived at prev_seg.stop_id at prev_seg["arrival_sec"]
                # and we depart at prev_seg["departure_sec"].
                # If the trip_id changed, it means at that stop we switched trips.
                waiting_time = (
                    prev_seg["departure_sec"] - prev_seg["arrival_sec"]
                ) / 60.0
                row["change_notice"] = (
                    "Change here! Wait {:.1f} minutes for the next trip.".format(
                        waiting_time
                    )
                )
            else:
                row["change_notice"] = "Change here! (Waiting time unavailable)"
        else:
            row["change_notice"] = ""

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

    return route, route_df


# =========================
# Example Usage:
# =========================
origin = "at:43:3162"  # Your origin stop_id
destination = "at:43:7105"  # Your destination stop_id
required_arrival_time_str = "13:30:00"  # Required arrival time

route, route_df = find_route_with_required_arrival(
    origin, destination, required_arrival_time_str
)

route_df.to_csv("GPT_route.csv")
