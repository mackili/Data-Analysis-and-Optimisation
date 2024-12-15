# %%
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point, MultiPoint, Polygon
import numpy as np

raster_out_of_range = gpd.read_file(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/ArcGIS/RASTER NO_WIEN Out of Range.shp"
)

print(raster_out_of_range.head())

pendler = pd.read_csv(
    "/Users/maciek/Documents/Dokumenty — MacBook Pro (Maciej)/Wirtschaftsuniversitat Wien/Year 5/DOA/Data-Analysis-and-Optimisation/pendler/20221031_pendelmatrix_250m_GroßraumWien_WU/20221031_pendelmatrix_250m.csv"
)


# %%
def __main__(pendler=pendler, raster=raster_out_of_range):
    result = {}
    result["All Commuters"] = pendler["pendlerInnen"].sum()
    result["Work Commuters"] = pendler["erwerbspendlerInnen"].sum()
    result["School Commuters"] = pendler["schuelerpendlerInnen"].sum()

    wo_out_of_range = pendler.set_index("wo").join(raster.set_index("gid"), how="left")
    wo_out_of_range = wo_out_of_range.set_index("ao").join(
        raster.set_index("gid"), how="left", rsuffix="2"
    )
    wo_out_of_range = wo_out_of_range[
        ~wo_out_of_range["gid"].isna() & ~wo_out_of_range["gid2"].isna()
    ]
    return result


print(__main__())

# %%
