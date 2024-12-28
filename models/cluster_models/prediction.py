from .settings import settings
from .src.predict import predict_model
from .src.tools.tools import list_files

import os
import pandas as pd
from pathlib import Path


async def prediction(data: pd.DataFrame):
    predictions = {}

    for kind in ["long", "short"]:
        models_list = list_files(
            directory=os.path.join(Path(__file__).parent.absolute(), 'models'),
            pattern=f'{"EURUSD=X"}_{settings.start}_{settings.end}_{settings.interval}_{kind}',
            extension=".joblib")

        prediction = predict_model(data=data,
                                   path=os.path.join(Path(__file__).parent.absolute(), 'models'),
                                   models=models_list,
                                   symbol="EURUSD=X",
                                   start=settings.start,
                                   end=settings.end,
                                   interval=settings.interval)
        predictions[kind] = prediction

    return predictions
