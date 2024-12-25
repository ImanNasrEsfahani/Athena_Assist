from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from pydantic import BaseModel

class BaseModelWithORM(BaseModel):
    class Config:
        orm_mode = True
        from_attributes = True  # Enable ORM compatibility
        arbitrary_types_allowed = True  # Allow arbitrary types
