import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

class ClusterPredictor:
    def __init__(self, model_path):
        model_data = self.load_model_data(model_path)
        self.model = model_data["model"]
        self.features = model_data["features"]
        self.model_name = model_data.get("name", "Unknown Model")
        self.model_abbr = model_data.get("abbr", "UNK")
        self.scaler = StandardScaler()

    def load_model_data(self, model_path):
        try:
            return joblib.load(model_path)
        except Exception as e:
            raise Exception(f"Error loading model data: {str(e)}")

    def preprocess_data(self, data):
        return self.scaler.fit_transform(data)

    def predict_cluster(self, data):
        preprocessed_data = self.preprocess_data(data)
        return self.model.predict(preprocessed_data)

    def predict_proba(self, data):
        preprocessed_data = self.preprocess_data(data)
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(preprocessed_data)
        else:
            raise AttributeError("This model doesn't support probability predictions")

    def get_features(self):
        return self.features

    def get_model_info(self):
        return {
            "name": self.model_name,
            "abbreviation": self.model_abbr,
            "features": self.features
        }

    def get_cluster_centers(self):
        if hasattr(self.model, 'cluster_centers_'):
            return self.model.cluster_centers_
        else:
            raise AttributeError("This model doesn't have cluster centers")
    
    def get_number_of_clusters(self):
        try:
            if hasattr(self.model, 'n_clusters'):
                return self.model.n_clusters
            elif hasattr(self.model, 'n_components'):
                return self.model.n_components
            elif hasattr(self.model, 'labels_'):
                # For algorithms like DBSCAN that determine clusters dynamically
                return len(np.unique(self.model.labels_))
            elif hasattr(self.model, 'children_'):
                # For hierarchical clustering
                return len(np.unique(self.model.labels_))
            else:
                # Return -1 instead of raising an error
                return -1
        except Exception:
            # Return -1 if any error occurs
            return -1
