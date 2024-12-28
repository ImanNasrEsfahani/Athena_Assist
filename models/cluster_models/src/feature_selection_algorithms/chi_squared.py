import pandas as pd
from scipy.stats import chi2_contingency


def chi_squared(data: pd.DataFrame, target: pd.DataFrame):

    # Sample data (contingency table)
    data = pd.DataFrame({
        'X1': [1, 1, 2, 2],
        'Y': [-1, 0, -1, 0]
    })

    # Create a contingency table
    contingency_table = pd.crosstab(data['X1'], data['Y'])

    # Perform Chi-squared test
    chi2_statistic, p_value, dof, expected = chi2_contingency(contingency_table)

    print(f"Chi-squared statistic: {chi2_statistic}, p-value: {p_value}")
    print(f"dof: {dof}, expected: {expected}")