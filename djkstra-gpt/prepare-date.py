import pandas as pd
import json
from collections import defaultdict
import os


def time_to_seconds(timestr):
    """Convert HH:MM:SS to seconds from midnight."""
    h, m, s = map(int, timestr.split(":"))
    return h * 3600 + m * 60 + s


# Make sure directories exist
os.makedirs("data", exist_ok=True)

# 1. Read GTFS Data
stops = pd.read_csv("GTFS_Simplified/stops.txt", dtype={"stop_id": str})
stop_times = pd.read_csv(
    "GTFS_Simplified/stop_times.txt", dtype={"trip_id": str, "stop_id": str}
)

# Ensure shape_dist_traveled is present
if "shape_dist_traveled" not in stop_times.columns:
    raise ValueError(
        "The stop_times.txt file must have a 'shape_dist_traveled' column."
    )

stop_times["arrival_sec"] = stop_times["arrival_time"].apply(time_to_seconds)
stop_times["departure_sec"] = stop_times["departure_time"].apply(time_to_seconds)

stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])

# 2. Build connections: (fstop, fdep, tstop, tarr, trip_id)
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

connections_df = pd.DataFrame(
    connections, columns=["fstop", "fdep", "tstop", "tarr", "trip_id"]
)

# Save connections to CSV for later reuse
connections_df.to_csv("djkstra-gpt/connections.csv", index=False)

# 3. Build arrivals_index: {tstop: [(fstop, fdep, tarr, trip_id), ...]}
arrivals_index = defaultdict(list)
for idx, row in connections_df.iterrows():
    tstop = row["tstop"]
    arrivals_index[tstop].append(
        [row["fstop"], int(row["fdep"]), int(row["tarr"]), row["trip_id"]]
    )

# Save arrivals_index to JSON
arrivals_index_dict = dict(arrivals_index)  # Convert defaultdict to normal dict
with open("djkstra-gpt/arrivals_index.json", "w") as f:
    json.dump(arrivals_index_dict, f)

print(
    "Preprocessing complete. 'connections.csv' and 'arrivals_index.json' saved in 'data' folder."
)
