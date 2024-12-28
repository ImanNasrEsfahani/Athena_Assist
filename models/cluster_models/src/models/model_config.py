# Models
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression


models = {
    # 'LogisticRegression': {
    #     "name": "LogisticRegression",
    #     "abbr": "LR",
    #     "model": LogisticRegression(),
    #     "params": {
    #         "C": [0.001, 0.01, 0.1, 1, 10, 100],
    #         "penalty": ['l2'],
    #         "solver": ['lbfgs'],
    #         "max_iter": [1000]
    #     }
    # },
    # 'GaussianNB': {
    #     "name": "GaussianNB",
    #     "abbr": "GNB",
    #     "model": GaussianNB(),
    #     "params": {
    #         "var_smoothing": [1e-9, 1e-8, 1e-7, 1e-6, 1e-5]
    #     }
    # },
    # 'SVC': {
    #     "name": "SVC",
    #     "abbr": "SVC",
    #     "model": SVC(),
    #     "params": {
    #         "C": [0.1, 1, 10, 100],
    #         "kernel": ['rbf', 'linear', 'poly'],
    #         "gamma": ['scale', 'auto', 0.1, 1]
    #     }
    # },
    'KNeighborsClassifier': {
        "name": "KNeighborsClassifier",
        "abbr": "KNN",
        "model": KNeighborsClassifier(),
        "params": {
            "n_neighbors": range(5, 11),
            "weights": ['uniform', 'distance'],
            "metric": ['euclidean', 'manhattan', 'minkowski']
        }
    },
    'DecisionTreeClassifier': {
        "name": "DecisionTreeClassifier",
        "abbr": "DT",
        "model": DecisionTreeClassifier(),
        "params": {
            "max_depth": [3,  5, 6, 7],
            "criterion": ['gini', 'entropy'],
            'min_samples_split': [6, 8],
            "min_samples_leaf": [4, 6],
            "max_features": ["sqrt"],
            "class_weight": ["balanced"],
            "ccp_alpha": [0.001],
        }
    },
    'ExtraTreeClassifier': {
        "name": "ExtraTreeClassifier",
        "abbr": "ET",
        "model": ExtraTreeClassifier(),
        "params": {
            "max_depth": [5, 6, 7],
            "min_samples_split": [10, 15],
            "min_samples_leaf": [4, 6, 8],
            "max_features": ['sqrt', 'log2', None],
            "criterion": ['gini', 'entropy']
        }
    },
    'RandomForestClassifier': {
        "name": "RandomForestClassifier",
        "abbr": "RF",
        "model": RandomForestClassifier(),
        "params": {
            'n_estimators': [100, 200, 300],
            'max_depth': [5, 6, 7],
            'min_samples_split': [10,15],
            'min_samples_leaf': [8, 12],
            'max_features': ['sqrt', 'log2']
        }
    },
    'BaggingClassifier': {
        "name": "BaggingClassifier",
        "abbr": "BagC",
        "model": BaggingClassifier(),
        "params": {
            "n_estimators": [10, 50, 100, 200],
            "max_samples": [0.7, 1.0],
            "max_features": [0.7, 1.0],
            "bootstrap": [True, False],
            "bootstrap_features": [True, False]
        }
    },
    'GradientBoostingClassifier': {
        "name": "GradientBoostingClassifier",
        "abbr": "GBoost",
        "model": GradientBoostingClassifier(),
        "params": {
            "n_estimators": [100, 200, 300],
            "learning_rate": [0.1],
            "max_depth": [3, 5, 7],
            "min_samples_split": [5, 10],
            "subsample": [0.8, 0.9]
        }
    },
    'AdaBoostClassifier': {
        "name": "AdaBoostClassifier",
        "abbr": "AdaBoost",
        "model": AdaBoostClassifier(),
        "params": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.1],
            "algorithm": ['SAMME']
        }
    },
    # 'GaussianMixture': {
    #     "name": "GaussianMixture",
    #     "abbr": "GM",
    #     "model": GaussianMixture,
    #     "params": {
    #         "n_components": [2, 3, 4, 5],
    #         "covariance_type": ['full', 'tied', 'diag', 'spherical'],
    #         "max_iter": [100, 200, 300],
    #         "n_init": [1, 5, 10]
    #     }
    # },
    # 'XGBoost': {
    #     "name": "XGBoost",
    #     "abbr": "XGBoost",
    #     "model": XGBClassifier,
    #     "params": {
    #         "max_depth": [3, 5, 7],
    #         "learning_rate": [0.01, 0.1, 0.3],
    #         "n_estimators": [100, 200, 300],
    #         "subsample": [0.8, 0.9, 1.0],
    #         "colsample_bytree": [0.8, 0.9, 1.0]
    #     }
    # },
    # 'AgglomerativeClustering': {
    #     "name": "AgglomerativeClustering",
    #     "abbr": "AggC",
    #     "model": AgglomerativeClustering,
    #     "params": {
    #         "n_clusters": [2, 3, 4, 5],
    #         "linkage": ['ward', 'complete', 'average'],
    #         "affinity": ['euclidean', 'l1', 'l2', 'manhattan']
    #     }
    # }
}
