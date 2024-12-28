import warnings
# Filter FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd
import numpy as np
import joblib, os
from tqdm import tqdm
from typing import Literal
from itertools import product, combinations, chain

# Models
from .models.model_config import models

# Model metrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, \
    classification_report, silhouette_score, calinski_harabasz_score, davies_bouldin_score, make_scorer

# Processing
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from datetime import datetime

import warnings
from sklearn.exceptions import UndefinedMetricWarning
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


# Define a function to process each combination
def process_combination(combination):
    # Replace this with your actual processing logic
    return f"Processed combination: {combination}"

def select_elements(lst, min_count=2, max_count=2):
    max_count = min(max_count, len(lst))
    selected_combinations = []
    for count in range(min_count, max_count + 1):
        selected_combinations.extend([list(combo) for combo in combinations(lst, count)])
    return selected_combinations

def train_model(positions: pd.DataFrame, features: pd.DataFrame, kind: str, symbol: str, start: str, end: str, interval: str):

    # Select features (X) and target variable (Y)
    features_old = ['stochastic%K_1h', 'stochastic%D_1h', "RSI_1h", "MACD_1h", 'Signal_Line_1h', 'MACD_Histogram_1h', 'ATR_1h', 'stochastic%K_4h', 'stochastic%D_4h', 'RSI_4h', 'MACD_4h', 'Signal_Line_4h', 'MACD_Histogram_4h', 'ATR_4h',
                'SMA_10_1h', 'SMA_20_1h', 'SMA_50_1h', 'EMA_10_1h', 'EMA_20_1h', 'EMA_50_1h', 'WMA_10_1h', 'WMA_20_1h', 'WMA_50_1h', 'SMA_10_4h', 'SMA_20_4h', 'SMA_50_4h', 'EMA_10_4h', 'EMA_20_4h', 'EMA_50_4h', 'WMA_10_4h', 'WMA_20_4h', 'WMA_50_4h']

    features = ['candle_stick_pattern', 'stochastic%K_1h', 'stochastic%D_1h', "stochastic_signal_1h", "RSI_1h", "MACD_1h", 'Signal_Line_1h', 'MACD_Histogram_1h', 'ATR_1h', 'stochastic%K_4h', 'stochastic%D_4h', "stochastic_signal_4h", 'RSI_4h', 'MACD_4h', 'Signal_Line_4h', 'MACD_Histogram_4h', 'ATR_4h',
                'EMA_10_1h', 'EMA_20_1h', 'EMA_50_1h', 'EMA_10_4h', 'EMA_20_4h', 'EMA_50_4h']

    
    use_all_features = True  # Set this to False if you want to use sub-features

    if use_all_features:
        combinations = [features]  # Use all features
    else:
        moving_average_indicators = ['EMA_10_1h', 'EMA_20_1h', 'EMA_50_1h', 'EMA_10_4h', 'EMA_20_4h', 'EMA_50_4h'] # 6
        RSI_MACD_indicators = ["RSI_1h", "MACD_1h", 'Signal_Line_1h', 'MACD_Histogram_1h', 'RSI_4h', 'MACD_4h', 'Signal_Line_4h', 'MACD_Histogram_4h'] # 8
        stocahastic_indicators = ['stochastic%K_1h', 'stochastic%D_1h', "stochastic_signal_1h", 'stochastic%K_4h', 'stochastic%D_4h', "stochastic_signal_4h"] # 6
        ATR_indicators = ['ATR_1h', 'ATR_4h'] # 2
        
        selected_moving_average = select_elements(moving_average_indicators)
        selected_RSI_MACD = select_elements(RSI_MACD_indicators)
        selected_stocahastic = select_elements(stocahastic_indicators)
        selected_ATR = select_elements(ATR_indicators)
        combinations = list(product(selected_moving_average, selected_RSI_MACD, selected_stocahastic, selected_ATR))

        
    target = "result"

    # Split the data into training and testing sets
    sample_analysis(positions[features], positions[target])

    # Create scorer to select best model in GridSearchCV
    custom_scorer = make_scorer(precision_class_1, greater_is_better=True)
    all_best_models_data = []

    # Print current date and time before the loop
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for model_name, model_info in tqdm(models.items(), desc="Various models", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {percentage:3.2f}% '):

        data = []
        best_precision = 0
        best_model_data = None
        best_model_estimator = None

        # print(f"Total number of combinations: {len(combinations)}")
        # print("\nSample results:")
        for index in tqdm(range(len(combinations)), desc="Various combination features", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {percentage:3.2f}% ', leave=False):
            
            if use_all_features:
                sub_features = combinations[0]  # All features
            else:
                result = combinations[index]
                sub_features = list(chain(*result))
                
            # result = combinations[index]
            # sub_features = list(chain(*result))
            x = positions[sub_features]
            y = positions[target]

            # Split the data into training and testing sets
            x_train, x_test, y_train, y_test = split_sample_with_balance(x, y)

            grid_search = GridSearchCV(estimator=model_info["model"],
                                       param_grid=model_info["params"],
                                       cv=7,
                                       scoring=custom_scorer,
                                       n_jobs=-1,
                                       verbose=0)
            # Train model
            grid_search.fit(x_train, y_train)

            # Evaluate model
            model_data = evaluate_model(model_name=model_name, grid_search=grid_search, x=x, x_test=x_test, y_test=y_test)
            model_data["features"] = sub_features
            model_data["index"] = index

            # Check if this model has the best precision so far
            if model_data["Best Precision"] > best_precision:
                best_precision = model_data["Best Precision"]
                best_model_data = model_data
                best_model_estimator = grid_search.best_estimator_

            data.append(model_data)

        # Save each model in seperate file name
        saving_model = {
            "name":    model_info["name"],
            "abbr":    model_info["abbr"],
            "model":    best_model_estimator,
            "features": data[-1]["features"]
        }

        joblib.dump(saving_model, os.path.join("models", f"{symbol}_{start}_{end}_{interval}_{kind}_{model_name}.joblib"))
        pd.DataFrame(data).to_csv(os.path.join("models", f"{symbol}_{start}_{end}_{interval}_{kind}_{data[0]['Model Name']}_models_comparisons.csv"), index=False)
        all_best_models_data.append(best_model_data)

    # Create a DataFrame from the list of model data
    df = pd.DataFrame(all_best_models_data)

    # Save the DataFrame as a CSV file
    df.to_csv(os.path.join("models", f"{symbol}_{start}_{end}_{interval}_{kind}_models_comparisons.csv"), index=False)
    print("Results have been saved to 'model_results.csv'")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0

def sample_analysis(x, y):
    print(f"Shape of X: {x.shape} Y: {y.shape}")
    print(f"Number of samples in X: {len(x)} Y: {len(y)}")
    print("Number of unique classes:", len(np.unique(y)))

    return 0

def evaluate_model(model_name: str, grid_search, x, x_test, y_test):
    # Prediction by model for test samples
    y_pred = grid_search.best_estimator_.predict(x_test)

    model_data = {
        "Model Name": model_name,
        "Best Score": round(grid_search.best_score_, 4),
        "Best Parameters": str(grid_search.best_params_),
        "Best Accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "Best Precision": round(precision_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        "Best Recall": round(recall_score(y_test, y_pred, average='weighted', zero_division=0), 4),
        "Best F1-Score": round(f1_score(y_test, y_pred, average='weighted', zero_division=0), 4),
    }

    # Clustering metrics
    unique_labels = np.unique(y_pred)
    if len(unique_labels) > 1:
        model_data["Silhouette"] = round(silhouette_score(x_test, y_pred), 4)
        model_data["Calinski_Harabasz"] = round(calinski_harabasz_score(x_test, y_pred), 4)
        model_data["Davies_Bouldin"] = round(davies_bouldin_score(x_test, y_pred), 4)
    else:
        model_data["Silhouette"] = -1
        model_data["Calinski_Harabasz"] = -1
        model_data["Davies_Bouldin"] = float("inf")

    # Create a dictionary to hold the flattened data
    flattened_data = {}

    # Iterate through the dictionary of classification_report and create new column names
    for key, value in classification_report(y_test, y_pred, output_dict=True).items():
        if isinstance(value, dict):
            for metric, score in value.items():
                flattened_data[f"{key}_{metric}"] = round(score, 4)
        else:
            flattened_data[key] = value

    model_data.update(flattened_data)

    # Add feature importance if available
    if hasattr(grid_search.best_estimator_, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': x.columns,
            'importance': grid_search.best_estimator_.feature_importances_
        })
        feature_importance = feature_importance.sort_values('importance', ascending=False)
        model_data["Feature Importance"] = feature_importance.to_string(index=False)
    elif hasattr(grid_search.best_estimator_, 'coef_'):
        feature_importance = pd.DataFrame({
            'feature': x.columns,
            'importance': abs(grid_search.best_estimator_.coef_[0])
        })
        feature_importance = feature_importance.sort_values('importance', ascending=False)
        model_data["Feature Importance"] = feature_importance.to_string(index=False)
    else:
        model_data["Feature Importance"] = "Not available"

    return model_data

def split_sample_with_balance(x, y, test_size=0.2, random_state=42):
    # Handle missing values in numeric features
    numeric_imputer = SimpleImputer(strategy='mean')
    x = pd.DataFrame(numeric_imputer.fit_transform(x), columns=x.columns)

    # Split the data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=random_state)

    # Scale features
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)


    # Apply SMOTE to balance the training set
    smote = SMOTE(random_state=random_state)
    X_train_resampled, y_train_resampled = smote.fit_resample(x_train_scaled, y_train)

    # print(f"""Number of samples in x_train: {len(x_train)} - y_train: {len(y_train)}""")
    # print(f"""Number of samples in x_test: {len(x_test)} - y_test: {len(y_test)}""")
    # unique_train, counts_train = np.unique(y_train, return_counts=True)
    # train_distribution = dict(zip(f"Class : {unique_train}", counts_train))
    # print("Training set distribution:", train_distribution)
    #
    # unique_test, counts_test = np.unique(y_test, return_counts=True)
    # test_distribution = dict(zip(f"Class : {unique_test}", counts_test))
    # print("Test set distribution:", test_distribution)

    return X_train_resampled, x_test_scaled, y_train_resampled, y_test

def precision_class_1(y_true, y_pred):
    return precision_score(y_true, y_pred, pos_label=1)