# %% [markdown]
# Author : https://github.com/amitrm/

# %% [markdown]
# #### Import Packages

import os
import folium as fl
import pandas as pd
from folium.plugins import MarkerCluster
import datetime
import numpy as np
from IPython.display import clear_output
import matplotlib.pyplot as plt
from collections import defaultdict, deque

# %% [markdown]
# #### Import Datasets
# Enforce string type for all IDs
stops = pd.read_csv("GTFS_Simplified/stops.txt", dtype={"stop_id": str})
stop_times = pd.read_csv(
    "GTFS_Simplified/stop_times.txt", dtype={"trip_id": str, "stop_id": str}
)

stop_times = stop_times.sort_values(
    ["trip_id", "stop_sequence"], ascending=[True, True]
).reset_index(drop=True)

stops.head(10)
stop_times.head(10)

# %% [markdown]
# #### Create a dataframe containing stop to stop travel time and distance

trip_list = list(stop_times.trip_id.unique())
data = pd.DataFrame(columns=["trip_id", "trip_seg", "fstop", "tstop", "time", "dist"])

counter = 0

for trip in trip_list:
    clear_output(wait=True)
    trip_df = stop_times[stop_times.trip_id == trip]

    trip_id_list = [trip] * (trip_df.shape[0] - 1)
    trip_seg_list = list(trip_df.stop_sequence.values)[:-1]
    fstop_list = list(trip_df.stop_id.values)[:-1]
    tstop_list = list(trip_df.stop_id.values)[1:]

    fstop_ts_list = list(trip_df.arrival_time.str.replace(" ", "0").values)[:-1]
    tstop_ts_list = list(trip_df.arrival_time.str.replace(" ", "0").values)[1:]

    fstop_dist = list(trip_df.shape_dist_traveled.values)[:-1]
    tstop_dist = list(trip_df.shape_dist_traveled.values)[1:]

    new_trip_df = pd.DataFrame(
        {
            "trip_id": trip_id_list,
            "trip_seg": trip_seg_list,
            "fstop": fstop_list,
            "tstop": tstop_list,
            "fstop_ts": fstop_ts_list,
            "tstop_ts": tstop_ts_list,
            "fstop_dist": fstop_dist,
            "tstop_dist": tstop_dist,
        }
    )
    new_trip_df["fstop_ts"] = new_trip_df["fstop_ts"].astype(str)
    new_trip_df["tstop_ts"] = new_trip_df["tstop_ts"].astype(str)

    new_trip_df["fstop_ts_hr"] = new_trip_df.fstop_ts.str[:2].astype(int)
    new_trip_df["fstop_ts_min"] = new_trip_df.fstop_ts.str[3:5].astype(int)
    new_trip_df["fstop_ts_sec"] = new_trip_df.fstop_ts.str[6:8].astype(int)
    new_trip_df["fstop_ts"] = (
        new_trip_df["fstop_ts_hr"] * 3600
        + new_trip_df["fstop_ts_min"] * 60
        + new_trip_df["fstop_ts_sec"]
    )

    new_trip_df["tstop_ts_hr"] = new_trip_df.tstop_ts.str[:2].astype(int)
    new_trip_df["tstop_ts_min"] = new_trip_df.tstop_ts.str[3:5].astype(int)
    new_trip_df["tstop_ts_sec"] = new_trip_df.tstop_ts.str[6:8].astype(int)
    new_trip_df["tstop_ts"] = (
        new_trip_df["tstop_ts_hr"] * 3600
        + new_trip_df["tstop_ts_min"] * 60
        + new_trip_df["tstop_ts_sec"]
    )

    new_trip_df["time"] = new_trip_df["tstop_ts"] - new_trip_df["fstop_ts"]
    new_trip_df["dist"] = new_trip_df["tstop_dist"] - new_trip_df["fstop_dist"]

    data = pd.concat([data, new_trip_df])

    counter = counter + 1
    print("Progress : {}%".format(np.round(counter * 100 / len(trip_list), 2)))
    print("Processing : {} of {} trips".format(counter, len(trip_list)))

# Ensure IDs remain strings
data["trip_id"] = data["trip_id"].astype(str)
data["trip_seg"] = data["trip_seg"].astype(
    int
)  # trip_seg can remain numeric if desired
data["fstop"] = data["fstop"].astype(str)
data["tstop"] = data["tstop"].astype(str)
data["time"] = data["time"].astype(int)
data["dist"] = data["dist"].astype(float)
data["stop_dummy"] = data.fstop.astype(str) + "-" + data.tstop.astype(str)

data = (
    data.sort_values(["time"], ascending=[True])
    .drop_duplicates(["stop_dummy"], keep="first")
    .drop(columns=["fstop_ts", "tstop_ts", "fstop_dist", "tstop_dist", "stop_dummy"])
)
data = data.sort_values(["trip_id", "trip_seg"], ascending=[True, True]).reset_index(
    drop=True
)

data = data[["trip_id", "trip_seg", "fstop", "tstop", "time", "dist"]]
data.to_csv("dijkstra_input.csv", index=False)
data.head(10)

# %% [markdown]
# #### Dijkstra Module


class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance


def dijkstra(graph, initial):
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node
        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            try:
                weight = current_weight + graph.distances[(min_node, edge)]
            except:
                continue
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path


def shortest_path(graph, origin, destination):
    visited, paths = dijkstra(graph, origin)
    full_path = deque()
    _destination = paths[destination]

    while _destination != origin:
        full_path.appendleft(_destination)
        _destination = paths[_destination]

    full_path.appendleft(origin)
    full_path.append(destination)

    return visited[destination], list(full_path)


# %% [markdown]
# #### Build the Network
data = pd.read_csv(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/dijkstra_input.csv"
)
sid = list(set(data.fstop.unique()) | set(data.tstop.unique()))

if __name__ == "__main__":
    graph = Graph()

    counter = 0
    for stop in sid:
        clear_output(wait=True)
        graph.add_node(stop)
        counter = counter + 1
        print("Stop : {} | {} of {}".format(stop, counter, len(sid)))
        print(type(stop))

    for index, row in data.iterrows():
        clear_output(wait=True)
        graph.add_edge(row["fstop"], row["tstop"], row["time"])
        print(row["fstop"], row["tstop"], row["time"])
        print("Segment : {} of {}".format(index + 1, data.shape[0]))

# %% [markdown]
# #### Find the Shortest Route


def find_shortest_route(fstop, tstop):
    result = shortest_path(graph, fstop, tstop)

    # No need to convert stop_ids to int. Keep them as strings.
    stops_df = pd.DataFrame(
        {"stop_id": result[1], "stop_seq": range(1, len(result[1]) + 1)}
    )

    # Ensure `stops["stop_id"]` is string for a successful merge
    stops_df = pd.merge(
        stops_df,
        stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]],
        on="stop_id",
        how="left",
    )

    dist_df = pd.DataFrame({"fstop": result[1][:-1], "tstop": result[1][1:]})

    dist_df = pd.merge(
        dist_df,
        data[["fstop", "tstop", "time", "dist"]],
        on=["fstop", "tstop"],
        how="left",
    )

    print(
        "Travel time     : {} ({} seconds)".format(
            str(datetime.timedelta(seconds=result[0])), result[0]
        )
    )
    print("Travel distance : {} meters".format(dist_df.dist.sum()))
    print(" ")
    print(stops_df[["stop_id", "stop_seq", "stop_name"]])
    return stops_df, dist_df


stops_df, dist_df = find_shortest_route("at:43:3162", "at:43:7105")

# %%
print(stops_df)
# %%
print(dist_df)


# %%
from itertools import combinations

pairs = list(combinations(stops["stop_id"].tolist(), 2))


# %%
def pair_exists_in_df(df, pair) -> bool:
    return not df[(df["fstop"] == pair[0]) & (df["tstop"] == pair[1])].empty


# Initialize an empty DataFrame to store all results
all_results = pd.DataFrame(columns=["fstop", "tstop", "time", "dist"])

# Iterate over each pair
for pair in pairs:
    if not pair_exists_in_df(all_results, pair):
        stops_df, dist_df = find_shortest_route(pair[0], pair[1])
        dist_df["fstop"] = pair[0]
        dist_df["tstop"] = pair[1]
        all_results = pd.concat([all_results, dist_df])

# Reset index of the final DataFrame
all_results.reset_index(drop=True, inplace=True)

all_results.to_csv("djkstra_output.csv")
# Print the final DataFrame
print(all_results)

# %% [markdown]
# #### Plot the Shortest Route on Map

gtfs_map = fl.Map(
    location=[
        stops_df["stop_lat"].astype(float).median(),
        stops_df["stop_lon"].astype(float).median(),
    ],
    tiles="Stamen Toner",
    attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.",
    zoom_start=15,
)
stop_clusters = MarkerCluster()
points = []

for row in stops_df.itertuples():
    point = (float(row.stop_lat), float(row.stop_lon))
    points.append(point)
    stop_clusters.add_child(
        fl.Marker(
            location=[float(row.stop_lat), float(row.stop_lon)], popup=row.stop_name
        )
    )

gtfs_map.add_child(stop_clusters)
gtfs_map.add_child(fl.PolyLine(points, color="red", weight=5, opacity=0.5))

# %%
