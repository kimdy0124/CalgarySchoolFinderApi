import os
import requests
from fastapi import APIRouter, HTTPException
from app.schemas import GeocodeIn

router = APIRouter(prefix="/geocode", tags=["geocode"])

@router.post("")
def geocode(payload: GeocodeIn):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_MAPS_API_KEY not set")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    resp = requests.get(url, params={"address": payload.address, "key": api_key}, timeout=10)
    data = resp.json()

    if data.get("status") != "OK" or not data.get("results"):
        raise HTTPException(status_code=400, detail=f"Geocode failed: {data.get('status')}")

    top = data["results"][0]
    loc = top["geometry"]["location"]
    return {"lat": loc["lat"], "lng": loc["lng"], "formatted_address": top.get("formatted_address")}
