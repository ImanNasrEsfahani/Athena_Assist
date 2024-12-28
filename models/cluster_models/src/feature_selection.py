import pandas as pd

from .feature_selection_algorithms.chi_squared import chi_squared
from .feature_selection_algorithms.hierarchical_clustering import feature_selection_by_hierarchical_clustering


def feature_selection(data: pd.DataFrame, features: list, n_clusters: int):
    data = data[100:]
    # data = data[features]
    print(data, " data")

    # grouped_features = feature_selection_by_hierarchical_clustering(data=data, features=features, n_clusters=n_clusters)

    chi_squared(data=data[features], target=data)

    exit("iman")
    # return grouped_features