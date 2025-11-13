use sqlx::{SqlitePool, sqlite::SqlitePoolOptions};
use anyhow::Result;

pub async fn init_db(database_url: &str) -> Result<SqlitePool> {
    let pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(database_url)
        .await?;
    
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            medical_record_number TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
        "#
    )
    .execute(&pool)
    .await?;
    
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS ed_visits (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            chief_complaint TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            esi_score_human INTEGER,
            esi_score_ai INTEGER,
            esi_confidence REAL,
            bed_number TEXT,
            current_status TEXT NOT NULL,
            door_to_provider_minutes INTEGER,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
        "#
    )
    .execute(&pool)
    .await?;
    
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS beds (
            id TEXT PRIMARY KEY,
            bed_number TEXT NOT NULL UNIQUE,
            zone TEXT NOT NULL,
            telemetry BOOLEAN NOT NULL,
            isolation BOOLEAN NOT NULL,
            occupied BOOLEAN NOT NULL,
            patient_id TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
        "#
    )
    .execute(&pool)
    .await?;
    
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            visit_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            acknowledged BOOLEAN NOT NULL,
            FOREIGN KEY (visit_id) REFERENCES ed_visits(id)
        )
        "#
    )
    .execute(&pool)
    .await?;
    
    let bed_count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM beds")
        .fetch_one(&pool)
        .await?;
    
    if bed_count == 0 {
        init_beds(&pool).await?;
    }
    
    log::info!("Database initialized successfully");
    Ok(pool)
}

async fn init_beds(pool: &SqlitePool) -> Result<()> {
    let zones = vec![
        ("monitored", true),
        ("monitored", true),
        ("monitored", true),
        ("monitored", true),
        ("fast-track", false),
        ("fast-track", false),
        ("fast-track", false),
        ("fast-track", false),
        ("main-ed", false),
        ("main-ed", false),
        ("main-ed", false),
        ("main-ed", false),
        ("trauma", true),
        ("trauma", true),
        ("isolation", false),
        ("isolation", false),
    ];
    
    for (i, (zone, telemetry)) in zones.iter().enumerate() {
        let bed_id = uuid::Uuid::new_v4().to_string();
        let bed_number = format!("Bed-{}", i + 1);
        
        sqlx::query(
            "INSERT INTO beds (id, bed_number, zone, telemetry, isolation, occupied, patient_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        .bind(&bed_id)
        .bind(&bed_number)
        .bind(zone)
        .bind(telemetry)
        .bind(zone == &"isolation")
        .bind(false)
        .bind::<Option<String>>(None)
        .execute(pool)
        .await?;
    }
    
    log::info!("Initialized 16 beds");
    Ok(())
}
