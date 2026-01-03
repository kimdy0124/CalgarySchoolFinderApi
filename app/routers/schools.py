from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import get_db
from typing import Optional

router = APIRouter(prefix="/schools", tags=["schools"])

@router.get("/nearby")
def nearby_schools(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0, ge=0.1, le=50.0),
    district_type: Optional[str] = Query(None),
    program_id: Optional[int] = Query(None),
    grade: Optional[int] = Query(None, ge=0, le=12),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    radius_m = radius_km * 1000.0

    sql = """
    SELECT
      s.school_id, s.name, s.address_line, s.postal_code, s.phone, s.email,
      s.latitude, s.longitude,
      d.district_id, d.name AS district_name, d.type AS district_type, d.website_url,
      es.status_name AS enrollment_status,
      (ST_Distance(s.geom, user_pt)) / 1000.0 AS distance_km
    FROM schools s
    JOIN districts d ON d.district_id = s.district_id
    LEFT JOIN enrollment_statuses es ON es.status_id = s.enrollment_status_id
    {program_join}
    CROSS JOIN (SELECT ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography AS user_pt) p
    WHERE s.geom IS NOT NULL
      AND ST_DWithin(s.geom, user_pt, :radius_m)
      {district_type_filter}
      {program_filter}
      {grade_filter}
    ORDER BY distance_km ASC
    LIMIT :limit;
    """

    program_join = ""
    program_filter = ""
    grade_filter = ""
    params = {"lat": lat, "lng": lng, "radius_m": radius_m, "limit": limit}

    if program_id is not None or grade is not None:
        program_join = "JOIN school_programs sp ON sp.school_id = s.school_id"
        if program_id is not None:
            program_filter += " AND sp.program_id = :program_id"
            params["program_id"] = program_id
        if grade is not None:
            grade_filter += " AND :grade BETWEEN COALESCE(sp.grade_min, -1) AND COALESCE(sp.grade_max, 99)"
            params["grade"] = grade

    district_type_filter = ""
    if district_type:
        district_type_filter = " AND d.type = :district_type"
        params["district_type"] = district_type

    final_sql = sql.format(
        program_join=program_join,
        district_type_filter=district_type_filter,
        program_filter=program_filter,
        grade_filter=grade_filter,
    )

    rows = db.execute(text(final_sql), params).mappings().all()
    return [
        {
            "school_id": r["school_id"],
            "name": r["name"],
            "address_line": r["address_line"],
            "postal_code": r["postal_code"],
            "phone": r["phone"],
            "email": r["email"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "enrollment_status": r["enrollment_status"],
            "distance_km": float(r["distance_km"]) if r["distance_km"] is not None else None,
            "district": {
                "district_id": r["district_id"],
                "name": r["district_name"],
                "type": r["district_type"],
                "website_url": r["website_url"],
            },
        }
        for r in rows
    ]

@router.get("/{school_id}")
def school_detail(school_id: int, db: Session = Depends(get_db)):
    r = db.execute(text("""
      SELECT
        s.school_id, s.name, s.address_line, s.postal_code, s.phone, s.email,
        s.latitude, s.longitude,
        d.district_id, d.name AS district_name, d.type AS district_type, d.website_url,
        es.status_name AS enrollment_status
      FROM schools s
      JOIN districts d ON d.district_id = s.district_id
      LEFT JOIN enrollment_statuses es ON es.status_id = s.enrollment_status_id
      WHERE s.school_id = :school_id;
    """), {"school_id": school_id}).mappings().first()

    if not r:
        raise HTTPException(status_code=404, detail="School not found")

    programs = db.execute(text("""
      SELECT p.program_id, p.name, p.category, sp.grade_min, sp.grade_max, sp.raw_label, sp.details_url
      FROM school_programs sp
      JOIN programs p ON p.program_id = sp.program_id
      WHERE sp.school_id = :school_id
      ORDER BY p.name ASC;
    """), {"school_id": school_id}).mappings().all()

    return {
        "school_id": r["school_id"],
        "name": r["name"],
        "address_line": r["address_line"],
        "postal_code": r["postal_code"],
        "phone": r["phone"],
        "email": r["email"],
        "latitude": r["latitude"],
        "longitude": r["longitude"],
        "enrollment_status": r["enrollment_status"],
        "district": {
            "district_id": r["district_id"],
            "name": r["district_name"],
            "type": r["district_type"],
            "website_url": r["website_url"],
        },
        "programs": [dict(p) for p in programs],
    }
