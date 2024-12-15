import pandas as pd
import math

distances = [500, 1000, 1500, 2000, 4000, 6000, 8000]

walking = 5
tram = 15.44


def main(distances=distances) -> pd.DataFrame:
    result = []
    for distance in distances:
        result.append(
            {
                "distance": distance,
                "walking": math.ceil((distance / 1000) / walking * 60),
                "tram": math.ceil((distance / 1000) / tram * 60),
            }
        )
    return pd.DataFrame(result)


if __name__ == "__main__":
    main().to_csv("DistanceTimeCalc.csv")
