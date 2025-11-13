# Lightning Triage™ Architecture

## System Overview

Lightning Triage is a hybrid Rust + Python system for AI-powered ER management.

## Components

### 1. Rust Backend (Actix-web)
- **Purpose**: Production API server, WebSocket hub, data persistence
- **Port**: 8000
- **Responsibilities**:
  - SQLite database management (patients, visits, beds, staff, alerts, agent_actions)
  - REST API endpoints for CRUD operations
  - WebSocket server for real-time dashboard updates
  - HTTP client to call Python inference service
  - Request routing, timeouts, retries, circuit breakers

### 2. Python Inference Service (FastAPI)
- **Purpose**: Real-time AI agent inference for clinical decisions
- **Port**: 8001
- **Responsibilities**:
  - 7 AI agents using Azure OpenAI (O3, O1, GPT-4.1)
  - ChromaDB integration for RAG (clinical guidelines, patient cases)
  - Agent Lightning tracer/emitter for collecting traces (feature-flagged)
  - Endpoints: `/agents/triage`, `/agents/resource`, `/agents/bed`, etc.

### 3. Python Training Service (FastAPI)
- **Purpose**: Offline agent training and optimization
- **Port**: 8002
- **Responsibilities**:
  - Agent Lightning integration for RL/APO training
  - Reads traces from LightningStore
  - Trains/optimizes agent prompts and policies
  - Writes updated models to model registry
  - Endpoints: `/training/start`, `/training/status`, `/models/latest`

### 4. React Frontend (Vite + TypeScript)
- **Purpose**: Real-time ER dashboard
- **Port**: 5173 (dev), deployed URL (prod)
- **Responsibilities**:
  - Dark theme UI with lightning effects
  - WebSocket connection to Rust backend
  - Components: AgentBar, BedGrid, AlertFeed, MetricsPanel
  - Real-time updates for bed status, agent activity, alerts

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 5173)                │
│  WebSocket ←→ Rust Backend for real-time updates            │
│  REST API ←→ Rust Backend for data queries                  │
└─────────────────────────────────────────────────────────────┘
                              ↕ WebSocket + REST
┌─────────────────────────────────────────────────────────────┐
│              Rust Backend (Actix-web, Port 8000)             │
│  - SQLite database (patients, visits, beds, alerts, etc.)   │
│  - WebSocket hub (broadcasts updates to frontend)           │
│  - HTTP client (calls Python inference service)             │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│         Python Inference Service (FastAPI, Port 8001)        │
│  - 7 AI Agents (Triage, Resource, Bed, etc.)                │
│  - Azure OpenAI integration (O3, O1, GPT-4.1)               │
│  - ChromaDB for RAG                                          │
│  - Agent Lightning tracer (optional, for collecting traces) │
└─────────────────────────────────────────────────────────────┘
                              ↕ Traces (async)
┌─────────────────────────────────────────────────────────────┐
│         Python Training Service (FastAPI, Port 8002)         │
│  - Agent Lightning training loops (RL/APO)                   │
│  - Reads traces from LightningStore                          │
│  - Writes optimized prompts to model registry                │
└─────────────────────────────────────────────────────────────┘
```

## Agent Communication Protocol

### Triage Agent
**Endpoint**: `POST /agents/triage`

**Request**:
```json
{
  "visit_id": "uuid",
  "patient_id": "uuid",
  "chief_complaint": "chest pain",
  "vital_signs": {
    "heart_rate": 105,
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90,
    "respiratory_rate": 20,
    "spo2": 96,
    "temperature": 98.6,
    "pain_scale": 7
  },
  "age": 58,
  "medical_history": ["hypertension", "diabetes"]
}
```

**Response**:
```json
{
  "esi_score": 2,
  "confidence": 0.94,
  "reasoning": "Cardiac symptoms with risk factors...",
  "recommended_actions": ["ECG", "Troponin", "Cardiology consult"],
  "agent_id": "triage",
  "model_version": "v1.0",
  "processing_time_ms": 850
}
```

### Resource Prediction Agent
**Endpoint**: `POST /agents/resource`

**Request**:
```json
{
  "visit_id": "uuid",
  "esi_score": 2,
  "chief_complaint": "chest pain",
  "age": 58,
  "vital_signs": {...}
}
```

**Response**:
```json
{
  "predicted_orders": [
    {"type": "lab", "name": "Troponin", "priority": "stat"},
    {"type": "imaging", "name": "Chest X-ray", "priority": "routine"},
    {"type": "consult", "name": "Cardiology", "priority": "urgent"}
  ],
  "predicted_los_hours": 4.5,
  "admission_probability": 0.65,
  "confidence": 0.88,
  "reasoning": "Based on similar cases...",
  "agent_id": "resource_prediction"
}
```

### Bed Assignment Agent
**Endpoint**: `POST /agents/bed`

**Request**:
```json
{
  "visit_id": "uuid",
  "esi_score": 2,
  "patient_requirements": {
    "telemetry": true,
    "isolation": false,
    "bariatric": false
  },
  "available_beds": [
    {"bed_id": "bed-8", "zone": "monitored", "telemetry": true, "occupied": false},
    {"bed_id": "bed-12", "zone": "fast-track", "telemetry": false, "occupied": false}
  ],
  "current_workload": {
    "monitored_zone": 0.75,
    "fast_track_zone": 0.50
  }
}
```

**Response**:
```json
{
  "assigned_bed": "bed-8",
  "zone": "monitored",
  "confidence": 0.91,
  "reasoning": "ESI-2 requires telemetry monitoring...",
  "alternative_beds": ["bed-10"],
  "agent_id": "bed_assignment"
}
```

## Database Schema (SQLite)

See `rust-backend/migrations/` for full schema.

Key tables:
- `patients` - Patient demographics
- `ed_visits` - ER visit records with ESI scores
- `vital_signs` - Time-series vitals
- `beds` - Bed inventory and status
- `staff` - Staff roster
- `orders` - Labs, imaging, consults
- `agent_actions` - Audit log of AI decisions
- `alerts` - Real-time alerts
- `predictions` - AI predictions vs actuals

## Model Registry

Location: `python-training/model_registry/`

Structure:
```
model_registry/
├── triage/
│   ├── v1.0.json (prompt template, system message, examples)
│   ├── v1.1.json
│   └── latest.json (symlink)
├── resource_prediction/
│   └── ...
└── versions.db (SQLite tracking table)
```

## Environment Variables

### Rust Backend (.env)
```
DATABASE_URL=sqlite:./lightning_triage.db
INFERENCE_SERVICE_URL=http://localhost:8001
TRAINING_SERVICE_URL=http://localhost:8002
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### Python Inference (.env)
```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_O3=o3
AZURE_OPENAI_DEPLOYMENT_O1=o1
AZURE_OPENAI_DEPLOYMENT_GPT41=gpt-4.1
CHROMADB_PATH=./chroma_db
MODEL_REGISTRY_PATH=../python-training/model_registry
AGL_ENABLED=false
```

### Python Training (.env)
```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
LIGHTNING_STORE_PATH=./lightning_store
MODEL_REGISTRY_PATH=./model_registry
```

## Development Workflow

1. Start Rust backend: `cd rust-backend && cargo run`
2. Start Python inference: `cd python-inference && poetry run uvicorn app.main:app --port 8001`
3. Start Python training: `cd python-training && poetry run uvicorn app.main:app --port 8002`
4. Start React frontend: `cd frontend && npm run dev`
5. Access dashboard: http://localhost:5173

## Deployment

- Rust backend: Compile to binary, deploy to VM/container
- Python services: Deploy via FastAPI deployment command
- Frontend: Build with `npm run build`, deploy static files

## Security

- SQLite encryption with SQLCipher (planned)
- JWT authentication for staff
- HTTPS/TLS for all traffic
- API rate limiting
- HIPAA audit logging in agent_actions table
