from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EURUSD_M15Create(BaseModel):
    timestamp:  datetime
    high:       float
    low:        float
    close:      float
    open:       float
    volume:     float

class EURUSD_M15Response(EURUSD_M15Create):
    id: int

    class Config:
        orm_mode = True

