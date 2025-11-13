"""
Synthetic data generator for Lightning Triage system testing.
Generates realistic patient data, vital signs, and ED scenarios.
"""

from faker import Faker
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

fake = Faker()

CHIEF_COMPLAINTS = [
    "Chest pain",
    "Shortness of breath",
    "Abdominal pain",
    "Headache",
    "Fever",
    "Nausea and vomiting",
    "Back pain",
    "Dizziness",
    "Weakness",
    "Fall",
    "Laceration",
    "Motor vehicle accident",
    "Altered mental status",
    "Seizure",
    "Syncope",
    "Difficulty breathing",
    "Cough",
    "Sore throat",
    "Urinary symptoms",
    "Leg pain",
]

MEDICAL_CONDITIONS = [
    "Hypertension",
    "Diabetes mellitus type 2",
    "Coronary artery disease",
    "Asthma",
    "COPD",
    "Atrial fibrillation",
    "Congestive heart failure",
    "Chronic kidney disease",
    "Hyperlipidemia",
    "Hypothyroidism",
    "Depression",
    "Anxiety",
    "Osteoarthritis",
    "GERD",
    "Previous MI",
]

BED_ZONES = {
    "monitored": {"count": 4, "telemetry": True, "isolation": False},
    "fast-track": {"count": 3, "telemetry": False, "isolation": False},
    "main-ed": {"count": 6, "telemetry": False, "isolation": False},
    "trauma": {"count": 2, "telemetry": True, "isolation": False},
    "isolation": {"count": 1, "telemetry": False, "isolation": True},
}


def generate_patient() -> Dict[str, Any]:
    """Generate a realistic synthetic patient"""
    return {
        "id": str(uuid.uuid4()),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=95).isoformat(),
        "medical_record_number": f"MRN{fake.random_number(digits=8, fix_len=True)}",
        "created_at": datetime.utcnow().isoformat(),
    }


def generate_vital_signs(esi_level: int) -> Dict[str, Any]:
    """Generate vital signs appropriate for ESI level"""
    
    if esi_level == 1:  # Critical
        return {
            "heart_rate": random.randint(120, 160),
            "blood_pressure_systolic": random.randint(70, 90),
            "blood_pressure_diastolic": random.randint(40, 60),
            "respiratory_rate": random.randint(28, 40),
            "spo2": random.randint(85, 92),
            "temperature": round(random.uniform(95.0, 96.5), 1),
            "pain_scale": random.randint(9, 10),
        }
    elif esi_level == 2:  # Emergent
        return {
            "heart_rate": random.randint(100, 120),
            "blood_pressure_systolic": random.randint(140, 180),
            "blood_pressure_diastolic": random.randint(85, 100),
            "respiratory_rate": random.randint(22, 28),
            "spo2": random.randint(92, 95),
            "temperature": round(random.uniform(100.5, 103.0), 1),
            "pain_scale": random.randint(7, 9),
        }
    elif esi_level == 3:  # Urgent
        return {
            "heart_rate": random.randint(80, 100),
            "blood_pressure_systolic": random.randint(120, 140),
            "blood_pressure_diastolic": random.randint(70, 85),
            "respiratory_rate": random.randint(16, 22),
            "spo2": random.randint(95, 97),
            "temperature": round(random.uniform(99.0, 100.4), 1),
            "pain_scale": random.randint(4, 7),
        }
    elif esi_level == 4:  # Less urgent
        return {
            "heart_rate": random.randint(65, 85),
            "blood_pressure_systolic": random.randint(110, 130),
            "blood_pressure_diastolic": random.randint(65, 80),
            "respiratory_rate": random.randint(14, 18),
            "spo2": random.randint(97, 99),
            "temperature": round(random.uniform(98.0, 99.0), 1),
            "pain_scale": random.randint(2, 4),
        }
    else:  # ESI 5 - Non-urgent
        return {
            "heart_rate": random.randint(60, 80),
            "blood_pressure_systolic": random.randint(110, 125),
            "blood_pressure_diastolic": random.randint(65, 75),
            "respiratory_rate": random.randint(12, 16),
            "spo2": random.randint(98, 100),
            "temperature": round(random.uniform(97.5, 98.6), 1),
            "pain_scale": random.randint(0, 2),
        }


def generate_ed_visit(patient_id: str = None) -> Dict[str, Any]:
    """Generate a realistic ED visit"""
    if not patient_id:
        patient_id = str(uuid.uuid4())
    
    esi_score = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 40, 30, 10])[0]
    chief_complaint = random.choice(CHIEF_COMPLAINTS)
    
    arrival_time = datetime.utcnow() - timedelta(minutes=random.randint(5, 240))
    
    return {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "chief_complaint": chief_complaint,
        "arrival_time": arrival_time.isoformat(),
        "esi_score_human": esi_score,
        "esi_score_ai": esi_score + random.choice([-1, 0, 0, 0, 1]),  # AI might differ slightly
        "esi_confidence": round(random.uniform(0.75, 0.98), 2),
        "bed_number": None,
        "current_status": random.choice(["Waiting", "With-Provider", "In-Treatment", "Awaiting-Results"]),
        "door_to_provider_minutes": random.randint(8, 45) if random.random() > 0.3 else None,
    }


def generate_bed_status() -> List[Dict[str, Any]]:
    """Generate complete bed status for all ED beds"""
    beds = []
    bed_number = 1
    
    for zone_name, zone_config in BED_ZONES.items():
        for i in range(zone_config["count"]):
            occupied = random.random() < 0.70  # 70% occupancy
            
            bed = {
                "id": str(uuid.uuid4()),
                "bed_number": f"Bed-{bed_number}",
                "zone": zone_name,
                "telemetry": zone_config["telemetry"],
                "isolation": zone_config["isolation"],
                "occupied": occupied,
                "patient_id": str(uuid.uuid4()) if occupied else None,
                "patient_name": None,
                "esi_score": None,
                "chief_complaint": None,
                "wait_time_minutes": None,
            }
            
            if occupied:
                esi_score = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 40, 30, 10])[0]
                bed["patient_name"] = f"{fake.last_name().upper()}, {fake.first_name()[0]}."
                bed["esi_score"] = esi_score
                bed["chief_complaint"] = random.choice(CHIEF_COMPLAINTS)
                bed["wait_time_minutes"] = random.randint(2, 180)
            
            beds.append(bed)
            bed_number += 1
    
    return beds


def generate_alert() -> Dict[str, Any]:
    """Generate a realistic AI alert"""
    alert_types = [
        {
            "type": "Patient Deterioration Detected",
            "severity": "critical",
            "icon": "🚨",
            "agent": "Clinical Deterioration Agent",
            "template": "Bed {bed} ({patient}) - BP dropping {bp1}→{bp2}, HR increasing {hr1}→{hr2}. Immediate MD re-evaluation required.",
        },
        {
            "type": "Bed Optimally Assigned",
            "severity": "low",
            "icon": "✅",
            "agent": "Bed Assignment Agent",
            "template": "New ESI-{esi} patient assigned to {zone} bed. Nurse {nurse} notified (lowest current acuity load).",
        },
        {
            "type": "Lab Results Delayed",
            "severity": "medium",
            "icon": "⚠️",
            "agent": "Wait Time Management Agent",
            "template": "Bed {bed} - Labs ordered {time}min ago, still pending. Consider follow-up with lab.",
        },
        {
            "type": "Bed Turnover Ready",
            "severity": "low",
            "icon": "🔄",
            "agent": "Resource Prediction Agent",
            "template": "Bed {bed} cleaned and ready for next patient. EVS completed {time}min ago.",
        },
        {
            "type": "Medication Supply Low",
            "severity": "medium",
            "icon": "⚠️",
            "agent": "Staffing Optimization Agent",
            "template": "{medication} stock below threshold. Pharmacy notified for restock.",
        },
        {
            "type": "Surge Risk Updated",
            "severity": "high",
            "icon": "📊",
            "agent": "Coordinator Agent",
            "template": "Next 4 hours: {risk} surge risk ({percent}%). Predicted {count} ESI-2 arrivals. Resource allocation optimized.",
        },
    ]
    
    alert_template = random.choice(alert_types)
    
    message = alert_template["template"].format(
        bed=random.randint(1, 16),
        patient=f"{fake.last_name().upper()}, {fake.first_name()[0]}.",
        bp1=random.randint(130, 150),
        bp2=random.randint(100, 120),
        hr1=random.randint(85, 105),
        hr2=random.randint(115, 135),
        esi=random.randint(2, 4),
        zone=random.choice(["monitored", "main ED", "fast-track"]),
        nurse=fake.first_name(),
        time=random.randint(15, 60),
        medication=random.choice(["Morphine", "Fentanyl", "Zofran", "Normal Saline", "Lactated Ringers"]),
        risk=random.choice(["Low", "Moderate", "High"]),
        percent=random.randint(15, 75),
        count=random.randint(5, 15),
    )
    
    return {
        "id": str(uuid.uuid4()),
        "visit_id": str(uuid.uuid4()),
        "alert_type": alert_template["type"],
        "severity": alert_template["severity"],
        "message": message,
        "agent_id": alert_template["agent"],
        "created_at": datetime.utcnow().isoformat(),
        "acknowledged": False,
        "icon": alert_template["icon"],
    }


def generate_batch_patients(count: int = 50) -> List[Dict[str, Any]]:
    """Generate a batch of patients for testing"""
    return [generate_patient() for _ in range(count)]


def generate_batch_visits(patient_ids: List[str] = None, count: int = 50) -> List[Dict[str, Any]]:
    """Generate a batch of ED visits"""
    if patient_ids:
        return [generate_ed_visit(patient_id) for patient_id in patient_ids[:count]]
    return [generate_ed_visit() for _ in range(count)]


def generate_batch_alerts(count: int = 20) -> List[Dict[str, Any]]:
    """Generate a batch of alerts"""
    return [generate_alert() for _ in range(count)]


if __name__ == "__main__":
    print("=== Synthetic Data Generator Test ===\n")
    
    print("Sample Patient:")
    print(generate_patient())
    print()
    
    print("Sample ED Visit:")
    print(generate_ed_visit())
    print()
    
    print("Sample Vital Signs (ESI-2):")
    print(generate_vital_signs(2))
    print()
    
    print("Sample Alert:")
    print(generate_alert())
    print()
    
    print("Bed Status (first 3):")
    beds = generate_bed_status()
    for bed in beds[:3]:
        print(bed)
