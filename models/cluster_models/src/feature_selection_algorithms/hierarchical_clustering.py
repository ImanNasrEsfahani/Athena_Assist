import pandas as pd
import plotly.graph_objects as go
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.preprocessing import StandardScaler


def feature_selection_by_hierarchical_clustering(data: pd.DataFrame, features: list, n_clusters: int):
    # Standardize the features
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(data)

    # Transpose the data so that features are rows
    feature_data_transposed = standardized_data.T

    # Perform hierarchical clustering
    Z = linkage(feature_data_transposed, method='ward')

    # Cut the dendrogram to get the desired number of clusters
    # Adjust 'n_clusters' as needed
    cluster_labels = fcluster(Z, n_clusters, criterion='maxclust')

    # Create a dictionary to store features grouped by cluster
    grouped_features = {i: [] for i in range(1, n_clusters + 1)}

    # Assign features to their respective clusters
    for feature, cluster in zip(features, cluster_labels):
        grouped_features[cluster].append(feature)

    # Print the grouped features
    for cluster, feature_list in grouped_features.items():
        print(f"Cluster {cluster}:")
        print(", ".join(feature_list))
        print()

    # Plot the dendrogram
    # plt.figure(figsize=(10, 7))
    # dendrogram(Z)
    # plt.title('Hierarchical Clustering Dendrogram')
    # plt.xlabel('Sample Index')
    # plt.ylabel('Distance')
    # plt.show()

    return grouped_features