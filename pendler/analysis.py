# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file_path = "20221031_pendelmatrix_250m_GroßraumWien_WU/20221031_pendelmatrix_250m.csv"


def import_data(path) -> pd.DataFrame:
    data = pd.read_csv(path)
    return data


def plot_histogram(data, column, transform="none") -> None:
    plt.figure(figsize=(10, 6))
    if transform == "log":
        plt.hist(np.log(data[column]), bins=30, edgecolor="k", alpha=0.7)
    else:
        plt.hist(data[column], bins=30, edgecolor="k", alpha=0.7)
    plt.title(f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()


# %%
data = import_data(path=file_path)
# %%
plot_histogram(data, "pendlerInnen")

# %%
plot_histogram(data, "pendlerInnen", "log")

# %%
