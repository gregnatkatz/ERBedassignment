"""
API endpoints for synthetic data generation.
Useful for testing and demo purposes.
"""

from fastapi import APIRouter
from typing import List
from .models import TriageRequest
from .synthetic_data import (
    generate_patient,
    generate_ed_visit,
    generate_vital_signs,
    generate_bed_status,
    generate_alert,
    generate_batch_patients,
    generate_batch_visits,
    generate_batch_alerts,
)

router = APIRouter(prefix="/synthetic", tags=["synthetic"])


@router.get("/patient")
async def get_synthetic_patient():
    """Generate a single synthetic patient"""
    return generate_patient()


@router.get("/patients/{count}")
async def get_synthetic_patients(count: int = 10):
    """Generate multiple synthetic patients"""
    return generate_batch_patients(count)


@router.get("/visit")
async def get_synthetic_visit():
    """Generate a single synthetic ED visit"""
    return generate_ed_visit()


@router.get("/visits/{count}")
async def get_synthetic_visits(count: int = 10):
    """Generate multiple synthetic ED visits"""
    return generate_batch_visits(count=count)


@router.get("/vital-signs/{esi_level}")
async def get_synthetic_vital_signs(esi_level: int):
    """Generate vital signs for a specific ESI level (1-5)"""
    if esi_level < 1 or esi_level > 5:
        return {"error": "ESI level must be between 1 and 5"}
    return generate_vital_signs(esi_level)


@router.get("/beds")
async def get_synthetic_bed_status():
    """Generate complete bed status for all ED beds"""
    return generate_bed_status()


@router.get("/alert")
async def get_synthetic_alert():
    """Generate a single synthetic alert"""
    return generate_alert()


@router.get("/alerts/{count}")
async def get_synthetic_alerts(count: int = 10):
    """Generate multiple synthetic alerts"""
    return generate_batch_alerts(count)


@router.post("/triage-request/{esi_level}")
async def get_synthetic_triage_request(esi_level: int):
    """Generate a complete synthetic triage request for testing"""
    if esi_level < 1 or esi_level > 5:
        return {"error": "ESI level must be between 1 and 5"}
    
    patient = generate_patient()
    visit = generate_ed_visit(patient["id"])
    vitals = generate_vital_signs(esi_level)
    
    return {
        "visit_id": visit["id"],
        "patient_id": patient["id"],
        "chief_complaint": visit["chief_complaint"],
        "vital_signs": vitals,
        "age": 58,
        "medical_history": ["hypertension", "diabetes"],
    }
