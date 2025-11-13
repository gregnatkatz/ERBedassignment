use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Serialize, Deserialize, FromRow)]
pub struct Patient {
    pub id: String,
    pub first_name: String,
    pub last_name: String,
    pub date_of_birth: String,
    pub medical_record_number: String,
    pub created_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreatePatient {
    pub first_name: String,
    pub last_name: String,
    pub date_of_birth: String,
    pub medical_record_number: String,
}

#[derive(Debug, Serialize, Deserialize, FromRow)]
pub struct EdVisit {
    pub id: String,
    pub patient_id: String,
    pub chief_complaint: String,
    pub arrival_time: String,
    pub esi_score_human: Option<i32>,
    pub esi_score_ai: Option<i32>,
    pub esi_confidence: Option<f64>,
    pub bed_number: Option<String>,
    pub current_status: String,
    pub door_to_provider_minutes: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateVisit {
    pub patient_id: String,
    pub chief_complaint: String,
}

#[derive(Debug, Serialize, Deserialize, FromRow)]
pub struct Bed {
    pub id: String,
    pub bed_number: String,
    pub zone: String,
    pub telemetry: bool,
    pub isolation: bool,
    pub occupied: bool,
    pub patient_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, FromRow)]
pub struct Alert {
    pub id: String,
    pub visit_id: String,
    pub alert_type: String,
    pub severity: String,
    pub message: String,
    pub agent_id: String,
    pub created_at: String,
    pub acknowledged: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TriageRequest {
    pub visit_id: String,
    pub patient_id: String,
    pub chief_complaint: String,
    pub vital_signs: VitalSigns,
    pub age: i32,
    pub medical_history: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VitalSigns {
    pub heart_rate: i32,
    pub blood_pressure_systolic: i32,
    pub blood_pressure_diastolic: i32,
    pub respiratory_rate: i32,
    pub spo2: i32,
    pub temperature: f64,
    pub pain_scale: i32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TriageResponse {
    pub esi_score: i32,
    pub confidence: f64,
    pub reasoning: String,
    pub recommended_actions: Vec<String>,
    pub agent_id: String,
    pub model_version: String,
    pub processing_time_ms: i32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BedRequestPayload {
    pub patient_name: String,
    pub esi_level: i32,
    pub chief_complaint: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BedRequestResponse {
    pub success: bool,
    pub message: String,
    pub assigned_bed: Option<String>,
    pub patient_id: Option<String>,
    pub visit_id: Option<String>,
}
