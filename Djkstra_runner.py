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
data = pd.read_csv("dijkstra_input.csv")
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

    # print(
    #     "Travel time     : {} ({} seconds)".format(
    #         str(datetime.timedelta(seconds=result[0])), result[0]
    #     )
    # )
    # print("Travel distance : {} meters".format(dist_df.dist.sum()))
    # print(" ")
    # print(stops_df[["stop_id", "stop_seq", "stop_name"]])
    return stops_df, dist_df


# stops_df, dist_df = find_shortest_route("at:43:3162", "at:43:7105")

# # %%
# print(stops_df)
# # %%
# print(dist_df)


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
    stops_df, dist_df = find_shortest_route(pair[0], pair[1])
    all_results = pd.concat([all_results, dist_df])

# Reset index of the final DataFrame
all_results.reset_index(drop=True, inplace=True)

all_results.to_csv("djkstra_output.csv")
