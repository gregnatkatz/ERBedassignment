use actix_web::{web, App, HttpServer, HttpResponse, Result};
use actix_cors::Cors;
use dotenv::dotenv;
use std::env;

mod models;
mod db;
mod agents;
mod websocket;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();
    env_logger::init();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let server_host = env::var("SERVER_HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
    let server_port = env::var("SERVER_PORT").unwrap_or_else(|_| "8000".to_string());
    
    let pool = db::init_db(&database_url).await.expect("Failed to initialize database");
    
    log::info!("Starting ContosoHealth Backend on {}:{}", server_host, server_port);
    
    HttpServer::new(move || {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);
            
        App::new()
            .wrap(cors)
            .app_data(web::Data::new(pool.clone()))
            .route("/", web::get().to(index))
            .route("/health", web::get().to(health))
            .route("/api/patients", web::get().to(agents::get_patients))
            .route("/api/patients", web::post().to(agents::create_patient))
            .route("/api/visits", web::get().to(agents::get_visits))
            .route("/api/visits", web::post().to(agents::create_visit))
            .route("/api/beds", web::get().to(agents::get_beds))
            .route("/api/alerts", web::get().to(agents::get_alerts))
            .route("/api/triage", web::post().to(agents::triage_patient))
            .route("/api/bed-request", web::post().to(agents::request_bed_assignment))
            .route("/ws", web::get().to(websocket::ws_index))
    })
    .bind(format!("{}:{}", server_host, server_port))?
    .run()
    .await
}

async fn index() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "service": "ContosoHealth Backend - A Faith Based Organization",
        "version": "1.0.0",
        "status": "operational"
    })))
}

async fn health() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy",
        "timestamp": chrono::Utc::now().to_rfc3339()
    })))
}
