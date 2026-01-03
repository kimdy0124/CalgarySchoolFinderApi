from fastapi import FastAPI
from app.routers import schools, districts, programs, geocode

app = FastAPI(title="Calgary School Finder API", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(schools.router)
app.include_router(districts.router)
app.include_router(programs.router)
app.include_router(geocode.router)
