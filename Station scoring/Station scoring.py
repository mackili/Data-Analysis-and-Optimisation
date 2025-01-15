import pandas as pd
from tqdm import tqdm
import numpy as np
from multiprocessing import Pool
from functools import partial

ATTRIBUTES = "Station scoring/Full Attributes.csv"


def main() -> pd.DataFrame:
    attr = pd.read_csv(ATTRIBUTES)


if __name__ == "__main__":
    main()
