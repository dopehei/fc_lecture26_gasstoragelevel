from pydantic import BaseModel


class GasStorageLevel(BaseModel):
    level: float
