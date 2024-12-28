import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

def maximum_liklihood_estimation(data: pd.DataFrame, target: pd.DataFrame):
    # Sample data
    data = pd.DataFrame({
        'X1': [1.0, 2.0, 3.0, 4.0],
        'X2': [5.0, 6.0, 7.0, 8.0],
        'Y': [-1.0 ,0.0 ,2.0 ,3.0]
    })

    # Define independent variables and dependent variable
    X = data[['X1', 'X2']]
    Y = data['Y']

    # Create and fit the logistic regression model
    model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=200)
    model.fit(X,Y)

    # Get estimated probabilities for each class
    probabilities = model.predict_proba(X)
    print("Estimated probabilities for each class:")
    print(probabilities)