from joblib import Parallel, delayed
import multiprocessing
import os
from joblib import Parallel, delayed, dump, load
import pandas as pd
import numpy as np


data = load(rf"models/EURUSD=X_2024-01-01_2024-06-30_1h_comparisons.sav")

data.to_csv(rf"models/EURUSD=X_2024-01-01_2024-06-30_1h_comparisons.csv")