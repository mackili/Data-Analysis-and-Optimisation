from webscraper import __request_vagonweb__, __extract_train_class__
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import time
import random

trips_path = "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/GTFS_Simplified/trips.txt"
delimiter = ","


def load_trips(trips_path, delimiter) -> pd.DataFrame:
    trips = pd.read_csv(trips_path, delimiter=delimiter)
    return trips


def extract_trip_identifier(trips_short_name) -> None | set:
    if pd.isna(trips_short_name):
        return None, None
    parts = trips_short_name.split()
    return parts[1], parts[0]


def process_trips(trips: pd.DataFrame) -> dict:
    trips_data = {}
    for trip_short_name in trips["trip_short_name"]:
        number, category = extract_trip_identifier(trip_short_name)
        if number and category:
            trips_data[number] = category
    keyset = trips_data.keys()
    print(len(keyset))
    return trips_data


trips = process_trips(load_trips(trips_path, delimiter))

tripstest = dict(list(trips.items())[3262:])


def scrape(trips: dict) -> dict:
    def standardize_category(category: str) -> str:
        if category == "S":
            return "R"
        else:
            return category

    i = 0
    class_storage = {}
    for train in trips.keys():
        category = standardize_category(trips.get(train))
        train_class = __extract_train_class__(
            __request_vagonweb__("ÖBB", category, train, 2024)
        )
        class_storage[train] = train_class
        i = i + 1
        print("Done " + str(i) + " out of " + str(len(trips.keys())))
    return class_storage


file_path = "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/vagonweb/webscraping_result.json"
retrieval_path = "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/vagonweb/retrieval_times.json"


def save_to_json(data: dict, file_path: str) -> None:
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def scrape_and_update(trips: dict, file_path: str) -> None:
    def standardize_category(category: str) -> str:
        if category == "S":
            return "R"
        else:
            return category

    def makeplot(retrieval_data, path) -> None:
        plt.figure(figsize=(10, 6))
        plt.plot(retrieval_data, marker="o")
        plt.title("Retrieval Times")
        plt.xlabel("Request Number")
        plt.ylabel("Time (seconds)")
        plt.grid(True)
        plt.savefig(
            f"/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/vagonweb/{path}.svg"
        )
        plt.savefig(
            f"/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/vagonweb/{path}.svg"
        )
        plt.show()

    try:
        with open(file_path, "r") as json_file:
            existing_data: dict = json.load(json_file)
        with open(
            retrieval_path,
            "r",
        ) as json_file:
            retrieval_times: dict = json.load(json_file)
    except FileNotFoundError:
        existing_data = {}
        retrieval_times = {}

    i = 3262
    for train in trips.keys():
        start_time = datetime.now()
        category = standardize_category(trips.get(train))
        train_class = __extract_train_class__(
            __request_vagonweb__("ÖBB", category, train, 2024)
        )
        if not (train_class) and category == "R":
            train_class = __extract_train_class__(
                __request_vagonweb__("ÖBB", "SB", train, 2024)
            )
        existing_data[train] = train_class
        delta = (datetime.now() - start_time).total_seconds()
        retrieval_times[train] = {"order": i, "time": delta}
        with open(file_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)
        with open(
            retrieval_path,
            "w",
        ) as json_file:
            json.dump(retrieval_times, json_file, indent=4)
        i += 1
        print(f"Done {i-3262} out of {len(trips.keys())}. Time elapsed: {delta}s")
        time.sleep(random.randrange(0, 360) / 100)

    # Save updated data back to JSON file
    with open(file_path, "w") as json_file:
        json.dump(existing_data, json_file, indent=4)
    with open(
        retrieval_path,
        "w",
    ) as json_file:
        json.dump(retrieval_times, json_file, indent=4)
    makeplot(retrieval_times.values(), "retrieval")


# with open(
#     retrieval_path,
#     "r",
# ) as json_file:
#     ret = json.load(json_file)
# with open(file_path, "r") as json_file:
#     ex: dict = json.load(json_file)
# trains = list(ex.keys())
# fin = {}
# i = 0
# for ret_item in ret:
#     fin[trains[i]] = {"order": i, "time": ret_item}
#     i = i + 1

# with open(
#     retrieval_path,
#     "w",
# ) as json_file:
#     json.dump(fin, json_file, indent=4)
# print(fin)

scrape_and_update(tripstest, file_path)
