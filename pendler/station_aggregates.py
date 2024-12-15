import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
import numpy as np

assignment_path = "Straßennetz/StationAssignment.csv"
pendler_matrix_path = (
    "pendler/20221031_pendelmatrix_250m_GroßraumWien_WU/20221031_pendelmatrix_250m.csv"
)


# def assigned_list(station: str, assignment: pd.DataFrame) -> list:
#     filtered = assignment[assignment.stop_id == station]
#     return filtered["raster"].to_list()


# def replace(station: str, replace: list, pendler: pd.DataFrame) -> pd.DataFrame:
#     return pendler.replace(to_replace=replace, value=station)


# def aggregate(pendler: pd.DataFrame) -> pd.DataFrame:
#     return pendler.groupby(["ao", "wo"], as_index=False).sum()


# def main() -> pd.DataFrame:
#     assignment = pd.read_csv(assignment_path, index_col=0)
#     pendler = pd.read_csv(pendler_matrix_path)

#     for station in assignment["stop_id"].unique():
#         to_replace = assigned_list(station=station, assignment=assignment)
#         pendler = replace(station=station, replace=to_replace, pendler=pendler)
#     return aggregate(pendler)


def assigned_list(station: str, assignment: pd.DataFrame) -> list:
    """
    Get the list of 'raster' values for a specific 'station' from the assignment DataFrame.
    """
    filtered = assignment[assignment.stop_id == station]
    return filtered["raster"].to_list()


def replace_chunk(
    chunk: pd.DataFrame, assignment: pd.DataFrame, unique_stations: list
) -> pd.DataFrame:
    """
    Replace the 'raster' values in a chunk of the DataFrame with corresponding 'station' values.
    """
    for station in unique_stations:
        to_replace = assigned_list(station, assignment)
        chunk = chunk.replace(to_replace=to_replace, value=station)
    return chunk


def aggregate(pendler: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate the DataFrame by unique pairs of 'ao' and 'wo', summing the 'value' column.
    """
    return pendler.groupby(["ao", "wo"], as_index=False).sum()


def main() -> pd.DataFrame:
    """
    Main function to process the assignment and pendler matrix using multicore processing.
    """
    # Load the data
    assignment = pd.read_csv(assignment_path, index_col=0)
    pendler = pd.read_csv(pendler_matrix_path)

    # Get unique stations
    unique_stations = assignment["stop_id"].unique()

    # Split the pendler DataFrame into chunks
    num_cores = cpu_count() - 2
    chunks = np.array_split(pendler, num_cores)

    # Process each chunk in parallel
    with Pool(num_cores) as pool:
        process_func = partial(
            replace_chunk, assignment=assignment, unique_stations=unique_stations
        )
        processed_chunks = pool.map(process_func, chunks)

    # Combine processed chunks and aggregate
    combined = pd.concat(processed_chunks, ignore_index=True)
    aggregated = aggregate(combined)

    return aggregated


if __name__ == "__main__":
    main().to_csv("pendler/aggregate_pendler.csv")
