import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def logistic_regression(data: pd.DataFrame, target: pd.DataFrame):
    # Sample data
    data = pd.DataFrame({
        'X1': [1, 2, 3, 4, 5],
        'X2': [2, 3, 4, 5, 6],
        'Y': [-1, 0, 2, 3, 4]
    })

    # Define independent variables and dependent variable
    X = data[['X1', 'X2']]
    Y = data['Y']

    # Split the data into training and test sets
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    # Create and fit the logistic regression model
    model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=200)
    model.fit(X_train, Y_train)

    # Make predictions
    Y_pred = model.predict(X_test)

    # Calculate accuracy
    accuracy = accuracy_score(Y_test, Y_pred)
    print(f"Accuracy: {accuracy:.2f}")