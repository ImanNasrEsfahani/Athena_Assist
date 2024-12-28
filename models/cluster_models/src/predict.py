from .models.ClusterPredictor import ClusterPredictor
from .feature import feature_extraction

import os.path
import pandas as pd

def predict_model(data: pd.DataFrame, path: str, models, symbol: str, start: str, end: str, interval: str):
    if len(models) == 0:
        return 0

    model_predictions = []
    probabilities_by_models = []

    for model in models:
        predictor = ClusterPredictor(os.path.join(path, model))
        model_info = predictor.get_model_info()
        model_features = list(predictor.get_features())

        # Feature extraction
        df = feature_extraction(processed_data=data, symbol=symbol, start=start, end=end, interval=interval)
        predicting_row = df.iloc[-1].to_frame().T
        selected_features = predicting_row[model_features]

        # Predict clusters
        clusters = predictor.predict_cluster(selected_features)
        
        # Store model results
        model_result = {
            'name': model_info['name'],
            'abbr': model_info['abbreviation'],
            'cluster': clusters[0].item(),
            'n_clusters': predictor.get_number_of_clusters(),
        }

        # Get probability predictions if supported
        try:
            probabilities = predictor.predict_proba(selected_features)
            probabilities_by_models.append({
                'abbr': model_info['abbreviation'],
                'probabilities': probabilities
            })
            model_result["probabilities"] = probabilities
        except AttributeError as e:
            print(f"Probabilities not available for {model_info['name']}: {str(e)}")

        model_predictions.append(model_result)

    # Calculate average
    avg_cluster = round(sum(m['cluster'] for m in model_predictions) / len(model_predictions), 2)

    result = {
        'models': model_predictions,
        'probabilities': probabilities_by_models,
        'average_cluster': avg_cluster
    }

    # print("Model Predictions:", model_predictions)
    # print("Average Cluster:", avg_cluster)

    return model_predictions


# def predict_model(data: pd.DataFrame, path: str, models, symbol: str, start: str, end: str, interval: str):
#     if len(models) == 0:
#         return 0

#     predicted_clusters_by_models = []
#     probabilities_by_models = []

#     for model in models:
#         # Initialize the predictor with the path to your saved model
#         print(model, "model")
#         predictor = ClusterPredictor(os.path.join(path, model))
#         model_features = list(predictor.get_features())

#         # make all features for new update data and then make a sub features based on features models
#         df = feature_extraction(processed_data=data, symbol=symbol, start=start, end=end, interval=interval)

#         predicting_row = df.iloc[-1].to_frame().T
#         selected_features = predicting_row[model_features]

#         # Predict clusters
#         clusters = predictor.predict_cluster(selected_features)
#         predicted_clusters_by_models.append(clusters[0].item())

#         # Get probability predictions (if supported)
#         try:
#             probabilities = predictor.predict_proba(selected_features)
#             probabilities_by_models.append(probabilities)
#             # print("Cluster probabilities:", probabilities)
#         except AttributeError as e:
#             print(str(e))

#     print(predicted_clusters_by_models, "predicted_clusters_by_models")

#     return round(sum(predicted_clusters_by_models) / len(predicted_clusters_by_models), 2)
