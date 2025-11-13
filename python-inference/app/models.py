from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime


class VitalSigns(BaseModel):
    heart_rate: int
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    respiratory_rate: int
    spo2: int
    temperature: float
    pain_scale: int = Field(ge=0, le=10)


class TriageRequest(BaseModel):
    visit_id: str
    patient_id: str
    chief_complaint: str
    vital_signs: VitalSigns
    age: int
    medical_history: List[str] = []


class ResourcePredictionRequest(BaseModel):
    visit_id: str
    esi_score: int
    chief_complaint: str
    age: int
    vital_signs: VitalSigns


class BedRequirements(BaseModel):
    telemetry: bool = False
    isolation: bool = False
    bariatric: bool = False


class AvailableBed(BaseModel):
    bed_id: str
    zone: str
    telemetry: bool
    occupied: bool


class BedAssignmentRequest(BaseModel):
    visit_id: str
    esi_score: int
    patient_requirements: BedRequirements
    available_beds: List[AvailableBed]
    current_workload: Dict[str, float]


class StaffingRequest(BaseModel):
    current_census: int
    esi_distribution: Dict[str, int]
    staff_count: int
    time_of_day: str


class WaitTimeRequest(BaseModel):
    visit_id: str
    esi_score: int
    current_wait_minutes: int
    pending_orders: List[str]


class DeteriorationRequest(BaseModel):
    visit_id: str
    patient_id: str
    vital_signs_history: List[VitalSigns]
    timestamps: List[str]
    current_esi: int


class TriageResponse(BaseModel):
    esi_score: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    recommended_actions: List[str]
    agent_id: str = "triage"
    model_version: str = "v1.0"
    processing_time_ms: int


class PredictedOrder(BaseModel):
    type: Literal["lab", "imaging", "consult", "medication"]
    name: str
    priority: Literal["stat", "urgent", "routine"]


class ResourcePredictionResponse(BaseModel):
    predicted_orders: List[PredictedOrder]
    predicted_los_hours: float
    admission_probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    agent_id: str = "resource_prediction"
    processing_time_ms: int


class BedAssignmentResponse(BaseModel):
    assigned_bed: str
    zone: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    alternative_beds: List[str] = []
    agent_id: str = "bed_assignment"
    processing_time_ms: int


class StaffingRecommendation(BaseModel):
    action: Literal["add_staff", "reallocate", "no_change"]
    details: str
    priority: Literal["high", "medium", "low"]


class StaffingResponse(BaseModel):
    recommendations: List[StaffingRecommendation]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    agent_id: str = "staffing_optimization"
    processing_time_ms: int


class WaitTimeResponse(BaseModel):
    bottleneck_identified: bool
    bottleneck_type: Optional[str] = None
    mitigation_strategies: List[str]
    estimated_delay_minutes: int
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    agent_id: str = "wait_time_management"
    processing_time_ms: int


class DeteriorationResponse(BaseModel):
    deterioration_detected: bool
    urgency_level: Literal["critical", "high", "medium", "low"]
    news2_score: Optional[int] = None
    recommended_actions: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    agent_id: str = "clinical_deterioration"
    processing_time_ms: int


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
