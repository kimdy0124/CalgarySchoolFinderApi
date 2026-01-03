from pydantic import BaseModel
from typing import Optional

class GeocodeIn(BaseModel):
    address: str

class GeocodeOut(BaseModel):
    lat: float
    lng: float
    formatted_address: Optional[str] = None
