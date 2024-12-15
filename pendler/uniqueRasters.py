import pandas as pd

file_path = (
    "pendler/20221031_pendelmatrix_250m_GroßraumWien_WU/20221031_pendelmatrix_250m.csv"
)
output_file_path = "pendler/unique_raster_ids.csv"


def get_unique_values(file_path: str, columns: list) -> pd.DataFrame:
    data = pd.read_csv(file_path)
    unique_values = set()
    for col in columns:
        unique_values.update(data[col].dropna().unique())
    # Create a DataFrame with a single column
    return pd.DataFrame({"unique_values": list(unique_values)})


def __main__() -> None:
    columns_to_extract = [
        "wo",
        "ao",
    ]
    unique_values_df = get_unique_values(file_path, columns_to_extract)

    # Save the result to a new CSV file
    unique_values_df.to_csv(output_file_path, index=False)
    print(f"Unique values saved to {output_file_path}")


if __name__ == "__main__":
    __main__()
