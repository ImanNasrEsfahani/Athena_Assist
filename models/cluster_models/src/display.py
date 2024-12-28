import pandas as pd
import plotly.graph_objects as go
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler


def plot_histograms(dataframe, columns, condition_column=None, condition_value=None):
    for column in columns:
        if column != condition_column:
            plt.figure(figsize=(10, 6))

            if condition_column and condition_value is not None:
                dataframe[column].hist(bins=30, alpha=0.6, label='All data')

                filtered_data_fail = dataframe[dataframe[condition_column] == 0]
                filtered_data_fail[column].hist(bins=30, alpha=0.6, label=f'{condition_column}=0')

                filtered_data = dataframe[dataframe[condition_column] == condition_value]
                filtered_data[column].hist(bins=30, alpha=0.6, label=f'{condition_column}={condition_value}')

                plt.legend()
            else:
                dataframe[column].hist(bins=30)

            plt.title(f'Histogram of {column}')
            plt.xlabel(column)
            plt.ylabel('Frequency')
            plt.show()

def plot_dendrogram(data: pd.DataFrame):
    print("dendrogram")

    data = data[100:]
    print(data, " data")

    features = ['stochastic%K_1h', 'stochastic%D_1h', "stochastic_signal_1h", "RSI_1h", "MACD_1h", 'Signal_Line_1h', 'MACD_Histogram_1h', 'ATR_1h', 'stochastic%K_4h', 'stochastic%D_4h', "stochastic_signal_4h", 'RSI_4h', 'MACD_4h', 'Signal_Line_4h', 'MACD_Histogram_4h', 'ATR_4h',
                'EMA_10_1h', 'EMA_20_1h', 'EMA_50_1h', 'EMA_10_4h', 'EMA_20_4h', 'EMA_50_4h']
    data = data[features]

    # Standardize the features
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(data)

    # Transpose the data so that features are rows
    feature_data_transposed = standardized_data.T

    # Perform hierarchical clustering
    Z = linkage(feature_data_transposed, method='ward')

    # Cut the dendrogram to get the desired number of clusters
    # Adjust 'n_clusters' as needed
    n_clusters = 7
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


def plot_candlestick(data, title="Candlestick Chart"):
    """
    Create a candlestick plot from OHLC data.

    Parameters:
    data (pd.DataFrame): DataFrame containing 'Date', 'Open', 'High', 'Low', 'Close' columns
    title (str): Title for the chart

    Returns:
    None: Displays the plot
    """
    # Ensure the data is sorted by date
    data = data.sort_values('datetime')

    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=data['datetime'],
                                         open=data['open'],
                                         high=data['high'],
                                         low=data['low'],
                                         close=data['close'])])

    # Update the layout
    fig.update_layout(title=title,
                      xaxis_title="Date",
                      yaxis_title="Price",
                      xaxis_rangeslider_visible=False)

    # Show the plot
    fig.show()

def plot_candlestick_with_positions(data: pd.DataFrame, positions: pd.DataFrame, kind: str, title="Candlestick Chart with Positions"):
    """
    Create a candlestick plot from OHLC data and overlay positions.

    Parameters:
    data (pd.DataFrame): DataFrame containing 'datetime', 'open', 'high', 'low', 'close' columns
    positions (pd.DataFrame): DataFrame containing position information
    title (str): Title for the chart

    Returns:
    None: Displays the plot
    """
    # Ensure the data is sorted by date
    data = data.sort_values('datetime')

    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=data['datetime'],
                                         open=data['open'],
                                         high=data['high'],
                                         low=data['low'],
                                         close=data['close'])])

    if kind == "long":
        positions_long = positions[positions['kind'] == kind]
        positions_long = positions_long[positions_long['result'] >= 2]
        entry_trace = create_position_markers(positions=positions_long, x=positions_long['datetime'], y=positions_long['open'], marker_type='triangle-up', color='green', size=10, name="long entry")
        exit_trace = create_position_markers(positions=positions_long, x=positions_long['exit_datetime'], y=positions_long['exit_price'], marker_type='triangle-up', color='green', size=10, name="long exit")
        line_trace = create_position_lines(positions=positions_long, color="gray", legend="long trace")
        fig.add_trace(entry_trace)
        fig.add_trace(exit_trace)
        fig.add_trace(line_trace)

    elif kind == "short":
        positions_short = positions[positions['kind'] == kind]
        entry_trace = create_position_markers(positions=positions_short, x=positions_short['datetime'], y=positions_short['open'], marker_type='triangle-down', color='red', size=10, name="short entry")
        exit_trace = create_position_markers(positions=positions_short, x=positions_short['exit_datetime'], y=positions_short['exit_price'], marker_type='triangle-down', color='red', size=10, name="short exit")
        line_trace = create_position_lines(positions=positions_short, color="gray", legend="short trace")
        fig.add_trace(entry_trace)
        fig.add_trace(exit_trace)
        fig.add_trace(line_trace)

    else:
        positions_long = positions[positions['kind'] == "long"]
        entry_trace = create_position_markers(positions=positions_long, x=positions_long['datetime'], y=positions_long['open'], marker_type='triangle-up', color=(0,200/255,0), size=9, name="long entry")
        exit_trace = create_position_markers(positions=positions_long, x=positions_long['exit_datetime'], y=positions_long['exit_price'], marker_type='square', color=(0,100/255,0), size=9, name="long exit")
        line_trace = create_position_lines(positions=positions_long, color="gray", legend="long trace")
        fig.add_trace(entry_trace)
        fig.add_trace(exit_trace)
        fig.add_trace(line_trace)

        positions_short = positions[positions['kind'] == "short"]
        entry_trace = create_position_markers(positions=positions_short, x=positions_short['datetime'], y=positions_short['open'], marker_type='triangle-down', color='red', size=10, name="short entry")
        exit_trace = create_position_markers(positions=positions_short, x=positions_long['exit_datetime'], y=positions_long['exit_price'], marker_type='square', color='red', size=10, name="short exit")
        line_trace = create_position_lines(positions=positions_short, color="gray", legend="short trace")
        fig.add_trace(entry_trace)
        fig.add_trace(exit_trace)
        fig.add_trace(line_trace)

    # Update the layout
    fig.update_layout(
        # title=title,
        # xaxis_title="Date",
        # yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10)
    )
    # Show the plot
    fig.show()

def create_position_markers(positions, x, y, marker_type, color, size, name):
    """
    Create position markers for entry or exit positions.

    Args:
    positions (pd.DataFrame): DataFrame containing position data
    marker_type (str): 'Entry' or 'Exit'
    color (str): Color of the markers

    Returns:
    go.Scatter: A Scatter object representing the position markers
    """
    # if marker_type == 'Entry':
    #     x = positions['datetime']
    #     y = positions['open']
    #     symbol = 'triangle-up'
    # elif marker_type == 'Exit':
    #     x = positions['exit_datetime']
    #     y = positions['exit_price']
    #     symbol = 'triangle-down'
    # else:
    #     raise ValueError("marker_type must be either 'Entry' or 'Exit'")

    hover_text = [
        f"Type: {kind}<br>"
        f"Open Price: {open_price}<br>"
        f"Open Date: {open_datetime}<br>"
        f"Close Price: {exit_price}<br>"
        f"Close Date: {exit_datetime}<br>"
        f"TP: {take_profit}<br>"
        f"SL: {stop_loss}<br>"
        f"Result: {result}"
        for kind, open_price, open_datetime, exit_price, exit_datetime, take_profit, stop_loss, result in
        zip(positions['kind'], positions['open'], positions['datetime'],
            positions['exit_price'], positions['exit_datetime'],
            positions['tp'], positions['sl'], positions['result'])
    ]

    return go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(size=size, symbol=marker_type, color=color),
        name=name,
        text=hover_text,
        hoverinfo='text'
    )

def create_position_lines(positions, color, legend):

    hover_text = [
        f"Type: {kind}<br>"
        f"Open Price: {open_price}<br>"
        f"Open Date: {open_datetime}<br>"
        f"Close Price: {exit_price}<br>"
        f"Close Date: {exit_datetime}<br>"
        f"TP: {take_profit}<br>"
        f"SL: {stop_loss}<br>"
        f"Result: {result}"
        for kind, open_price, open_datetime, exit_price, exit_datetime, take_profit, stop_loss, result in
        zip(positions['kind'], positions['open'], positions['datetime'],
            positions['exit_price'], positions['exit_datetime'],
            positions['tp'], positions['sl'], positions['result'])
    ]

    return  go.Scatter(
        x=positions[['datetime', 'exit_datetime']].values.flatten(),
        y=positions[['open', 'exit_price']].values.flatten(),
        mode='lines+markers',
        line=dict(color='gray', width=1),
        marker=dict(size=0),
        name=legend,
        showlegend=True,
        text=hover_text
    )
