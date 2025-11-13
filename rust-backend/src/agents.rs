use actix_web::{web, HttpResponse, Result};
use sqlx::SqlitePool;
use crate::models::*;
use std::env;

pub async fn get_patients(pool: web::Data<SqlitePool>) -> Result<HttpResponse> {
    let patients = sqlx::query_as::<_, Patient>("SELECT * FROM patients ORDER BY created_at DESC LIMIT 100")
        .fetch_all(pool.get_ref())
        .await
        .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    Ok(HttpResponse::Ok().json(patients))
}

pub async fn create_patient(
    pool: web::Data<SqlitePool>,
    patient: web::Json<CreatePatient>
) -> Result<HttpResponse> {
    let id = uuid::Uuid::new_v4().to_string();
    let created_at = chrono::Utc::now().to_rfc3339();
    
    sqlx::query(
        "INSERT INTO patients (id, first_name, last_name, date_of_birth, medical_record_number, created_at) 
         VALUES (?, ?, ?, ?, ?, ?)"
    )
    .bind(&id)
    .bind(&patient.first_name)
    .bind(&patient.last_name)
    .bind(&patient.date_of_birth)
    .bind(&patient.medical_record_number)
    .bind(&created_at)
    .execute(pool.get_ref())
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    let new_patient = Patient {
        id,
        first_name: patient.first_name.clone(),
        last_name: patient.last_name.clone(),
        date_of_birth: patient.date_of_birth.clone(),
        medical_record_number: patient.medical_record_number.clone(),
        created_at,
    };
    
    Ok(HttpResponse::Created().json(new_patient))
}

pub async fn get_visits(pool: web::Data<SqlitePool>) -> Result<HttpResponse> {
    let visits = sqlx::query_as::<_, EdVisit>("SELECT * FROM ed_visits ORDER BY arrival_time DESC LIMIT 100")
        .fetch_all(pool.get_ref())
        .await
        .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    Ok(HttpResponse::Ok().json(visits))
}

pub async fn create_visit(
    pool: web::Data<SqlitePool>,
    visit: web::Json<CreateVisit>
) -> Result<HttpResponse> {
    let id = uuid::Uuid::new_v4().to_string();
    let arrival_time = chrono::Utc::now().to_rfc3339();
    
    sqlx::query(
        "INSERT INTO ed_visits (id, patient_id, chief_complaint, arrival_time, current_status) 
         VALUES (?, ?, ?, ?, ?)"
    )
    .bind(&id)
    .bind(&visit.patient_id)
    .bind(&visit.chief_complaint)
    .bind(&arrival_time)
    .bind("Waiting")
    .execute(pool.get_ref())
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    let new_visit = EdVisit {
        id,
        patient_id: visit.patient_id.clone(),
        chief_complaint: visit.chief_complaint.clone(),
        arrival_time,
        esi_score_human: None,
        esi_score_ai: None,
        esi_confidence: None,
        bed_number: None,
        current_status: "Waiting".to_string(),
        door_to_provider_minutes: None,
    };
    
    Ok(HttpResponse::Created().json(new_visit))
}

pub async fn get_beds(pool: web::Data<SqlitePool>) -> Result<HttpResponse> {
    let beds = sqlx::query_as::<_, Bed>("SELECT * FROM beds ORDER BY bed_number")
        .fetch_all(pool.get_ref())
        .await
        .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    Ok(HttpResponse::Ok().json(beds))
}

pub async fn get_alerts(pool: web::Data<SqlitePool>) -> Result<HttpResponse> {
    let alerts = sqlx::query_as::<_, Alert>(
        "SELECT * FROM alerts WHERE acknowledged = 0 ORDER BY created_at DESC LIMIT 50"
    )
    .fetch_all(pool.get_ref())
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    Ok(HttpResponse::Ok().json(alerts))
}

pub async fn triage_patient(
    pool: web::Data<SqlitePool>,
    request: web::Json<TriageRequest>
) -> Result<HttpResponse> {
    let inference_url = env::var("INFERENCE_SERVICE_URL")
        .unwrap_or_else(|_| "http://localhost:8001".to_string());
    
    let visit_id = request.visit_id.clone();
    let request_data = request.into_inner();
    
    let client = reqwest::Client::new();
    let response = client
        .post(format!("{}/agents/triage", inference_url))
        .json(&request_data)
        .send()
        .await
        .map_err(|e| actix_web::error::ErrorInternalServerError(format!("Failed to call inference service: {}", e)))?;
    
    if !response.status().is_success() {
        return Err(actix_web::error::ErrorInternalServerError("Inference service returned error"));
    }
    
    let triage_response: TriageResponse = response
        .json()
        .await
        .map_err(|e| actix_web::error::ErrorInternalServerError(format!("Failed to parse response: {}", e)))?;
    
    sqlx::query(
        "UPDATE ed_visits SET esi_score_ai = ?, esi_confidence = ? WHERE id = ?"
    )
    .bind(triage_response.esi_score)
    .bind(triage_response.confidence)
    .bind(&visit_id)
    .execute(pool.get_ref())
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
    
    Ok(HttpResponse::Ok().json(triage_response))
}

pub async fn request_bed_assignment(
    pool: web::Data<SqlitePool>,
    payload: web::Json<BedRequestPayload>,
) -> Result<HttpResponse> {
    let payload = payload.into_inner();
    
    let patient_id = uuid::Uuid::new_v4().to_string();
    let visit_id = uuid::Uuid::new_v4().to_string();
    
    let name_parts: Vec<&str> = payload.patient_name.split(',').collect();
    let (last_name, first_name) = if name_parts.len() >= 2 {
        (name_parts[0].trim(), name_parts[1].trim().trim_end_matches('.'))
    } else {
        (payload.patient_name.as_str(), "Unknown")
    };
    
    let mrn = format!("MRN{:08}", rand::random::<u32>() % 100000000);
    
    let insert_patient = sqlx::query(
        "INSERT INTO patients (id, first_name, last_name, date_of_birth, medical_record_number, created_at)
         VALUES (?, ?, ?, ?, ?, ?)"
    )
    .bind(&patient_id)
    .bind(first_name)
    .bind(last_name)
    .bind("1980-01-01")
    .bind(&mrn)
    .bind(chrono::Utc::now().to_rfc3339())
    .execute(pool.get_ref())
    .await;
    
    if let Err(e) = insert_patient {
        log::error!("Failed to insert patient: {}", e);
        return Ok(HttpResponse::InternalServerError().json(BedRequestResponse {
            success: false,
            message: format!("Failed to create patient: {}", e),
            assigned_bed: None,
            patient_id: None,
            visit_id: None,
        }));
    }
    
    let arrival_time = chrono::Utc::now().to_rfc3339();
    let insert_visit = sqlx::query(
        "INSERT INTO ed_visits (id, patient_id, chief_complaint, arrival_time, esi_score_human, current_status)
         VALUES (?, ?, ?, ?, ?, ?)"
    )
    .bind(&visit_id)
    .bind(&patient_id)
    .bind(&payload.chief_complaint)
    .bind(&arrival_time)
    .bind(payload.esi_level)
    .bind("Waiting")
    .execute(pool.get_ref())
    .await;
    
    if let Err(e) = insert_visit {
        log::error!("Failed to insert visit: {}", e);
        return Ok(HttpResponse::InternalServerError().json(BedRequestResponse {
            success: false,
            message: format!("Failed to create visit: {}", e),
            assigned_bed: None,
            patient_id: Some(patient_id),
            visit_id: None,
        }));
    }
    
    let available_beds: Vec<(String, String, bool, bool)> = sqlx::query_as(
        "SELECT bed_number, zone, telemetry, isolation FROM beds WHERE occupied = 0 LIMIT 10"
    )
    .fetch_all(pool.get_ref())
    .await
    .unwrap_or_default();
    
    let final_bed = if let Some((bed_num, _, _, _)) = available_beds.first() {
        bed_num.clone()
    } else {
        "Bed-1".to_string()
    };
    
    let update_bed = sqlx::query(
        "UPDATE beds SET occupied = 1, patient_id = ? WHERE bed_number = ?"
    )
    .bind(&patient_id)
    .bind(&final_bed)
    .execute(pool.get_ref())
    .await;
    
    if let Err(e) = update_bed {
        log::warn!("Failed to update bed: {}", e);
    }
    
    let update_visit = sqlx::query(
        "UPDATE ed_visits SET bed_number = ?, current_status = ? WHERE id = ?"
    )
    .bind(&final_bed)
    .bind("In-Treatment")
    .bind(&visit_id)
    .execute(pool.get_ref())
    .await;
    
    if let Err(e) = update_visit {
        log::warn!("Failed to update visit with bed: {}", e);
    }
    
    Ok(HttpResponse::Ok().json(BedRequestResponse {
        success: true,
        message: format!("Bed {} assigned to {} (ESI-{})", final_bed, payload.patient_name, payload.esi_level),
        assigned_bed: Some(final_bed),
        patient_id: Some(patient_id),
        visit_id: Some(visit_id),
    }))
}
