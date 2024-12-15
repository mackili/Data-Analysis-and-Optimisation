# %%
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point, MultiPoint, Polygon
import numpy as np
from multiprocessing import Pool, cpu_count

raster_points_Wien = gpd.read_file(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/ArcGIS/RasterPointsWien_ExportFeatures.shp"
)
print(len(raster_points_Wien))
raster_points_NO = gpd.read_file(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/ArcGIS/RasterPointsNO.shp"
)
raster_points_ALL = gpd.read_file(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/ArcGIS/RasterPointsALL.shp"
)
distance_bands_Wien = gpd.read_file(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/ArcGIS/DistanceAreasWien.shp"
)
distance_bands_NO = gpd.read_file(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/ArcGIS/Stops_MultipleRingBuffer_ExportFeatures.shp"
)

# %%
print(raster_points_Wien.crs)
distance_bands_Wien = distance_bands_Wien.to_crs(raster_points_Wien.crs)
raster_points_NO = raster_points_NO.to_crs(raster_points_Wien.crs)
distance_bands_NO = distance_bands_NO.to_crs(raster_points_Wien.crs)

# %%

raster_join_wien = raster_points_Wien.sjoin(distance_bands_Wien, how="left")
raster_join_no = raster_points_NO.sjoin(distance_bands_NO, how="left")
print(raster_join_wien.head())
print(f"Vienna data with {len(raster_join_wien)} rows")

# %%
print(raster_join_no.head())
print(f"Lower Austria data with {len(raster_join_no)} rows")

# %%

raster_assigment_union = pd.concat([raster_join_no, raster_points_Wien])
print(f"Unioned data for {len(raster_assigment_union)} assignmens.")
print(raster_assigment_union.head())


# %%
def GetStationsVienna(df=distance_bands_Wien) -> list:
    pattern = r"(at:\d+:\d+).*?(\d+ - \d+)"
    df[["station_code", "range"]] = df["Name"].str.extract(pattern)
    station_codes = df["station_code"].unique().tolist()
    return station_codes


def GetStationsNO(df=distance_bands_NO) -> list:
    station_codes = df["GStopID"].unique().tolist()
    return station_codes


def DistanceMatrixVienna(
    rasters=raster_join_wien, pattern=r"(at:\d+:\d+).*?(\d+ - \d+)"
) -> list:
    # Extract "station_code" and "range" from the "Name" column
    extracted = rasters["Name"].str.extract(pattern)
    rasters["station_code"] = extracted[0]  # Matches the first group (e.g., at:49:94)
    rasters["range"] = extracted[1]  # Matches the second group (e.g., 6000 - 8000)

    # Filter out rows where 'FromBreak' is NaN
    rasters = rasters.dropna(subset=["FromBreak"])

    # Group by 'gid' and construct dictionaries
    matrix = [
        {"gid": gid, **dict(zip(group["station_code"], group["FromBreak"]))}
        for gid, group in rasters.groupby("gid")
    ]

    return matrix


def DistanceMatrixLowerAustria(rasters=raster_join_no, stations=None) -> list:
    # Filter out rows where 'distance' is NaN
    rasters = rasters.dropna(subset=["distance"])

    # Group by 'gid' and construct dictionaries for each group
    matrix = [
        {"gid": gid, **dict(zip(group["GStopID"], group["distance"]))}
        for gid, group in rasters.groupby("gid")
    ]

    return matrix


dist_vienna = DistanceMatrixVienna()
dist_lower_austria = DistanceMatrixLowerAustria()
OD_Vienna = pd.DataFrame(dist_vienna)
OD_Vienna.to_csv("Straßennetz/WienMatrix.csv")
OD_LoverAustria = pd.DataFrame(dist_lower_austria)
OD_LoverAustria.to_csv("Straßennetz/NOMatrix.csv")


def MergeLists(base=dist_lower_austria, to_merge=dist_vienna, key="gid"):
    # Create a dictionary to hold the merged results
    # Convert lists of dictionaries into DataFrames
    df1 = pd.DataFrame(base).set_index(key)
    df2 = pd.DataFrame(to_merge).set_index(key)

    # Merge the two DataFrames on the key, preserving all data
    merged_df = df1.combine_first(df2).reset_index()

    # Convert the merged DataFrame back to a list of dictionaries
    merged_list = merged_df.to_dict(orient="records")
    return merged_list


OD_All = pd.DataFrame(MergeLists())
OD_All.to_csv("Straßennetz/GrossraumWienMatrix.csv")


def exclude_empty_rows(df=OD_All, key="gid") -> pd.DataFrame:
    # Check if all columns except the key column are NaN
    non_empty_mask = ~df.drop(columns=[key]).isna().all(axis=1)

    # Filter the DataFrame to keep only rows that are not completely empty
    non_empty_rows = df[non_empty_mask]
    return non_empty_rows


rasters_with_station = exclude_empty_rows()
rasters_with_station.to_csv("Straßennetz/WithStation.csv")
