from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv

from .models import (
    TriageRequest, TriageResponse,
    ResourcePredictionRequest, ResourcePredictionResponse,
    BedAssignmentRequest, BedAssignmentResponse,
    StaffingRequest, StaffingResponse,
    WaitTimeRequest, WaitTimeResponse,
    DeteriorationRequest, DeteriorationResponse,
    HealthResponse
)
from .agents import (
    TriageAgent,
    ResourcePredictionAgent,
    BedAssignmentAgent,
    StaffingAgent,
    WaitTimeAgent,
    DeteriorationAgent
)
from .api_synthetic import router as synthetic_router
from .training.lightning_trainer import get_trainer

load_dotenv()

app = FastAPI(
    title="ContosoHealth Inference Service",
    description="A Faith Based Organization - AI-powered ER management agent inference service with Agent Lightning training",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(synthetic_router)

# Initialize agents
triage_agent = TriageAgent()
resource_agent = ResourcePredictionAgent()
bed_agent = BedAssignmentAgent()
staffing_agent = StaffingAgent()
wait_time_agent = WaitTimeAgent()
deterioration_agent = DeteriorationAgent()


@app.get("/")
async def root():
    return {
        "service": "ContosoHealth Inference Service - A Faith Based Organization",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "triage": "operational",
            "resource_prediction": "operational",
            "bed_assignment": "operational",
            "staffing": "operational",
            "wait_time": "operational",
            "deterioration": "operational"
        }
    )


@app.post("/agents/triage", response_model=TriageResponse)
async def triage(request: TriageRequest):
    try:
        return triage_agent.process(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/resource", response_model=ResourcePredictionResponse)
async def resource_prediction(request: ResourcePredictionRequest):
    try:
        return resource_agent.process(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/bed", response_model=BedAssignmentResponse)
async def bed_assignment(request: BedAssignmentRequest):
    try:
        return bed_agent.process(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/staffing", response_model=StaffingResponse)
async def staffing_optimization(request: StaffingRequest):
    try:
        return staffing_agent.process(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/wait-time", response_model=WaitTimeResponse)
async def wait_time_management(request: WaitTimeRequest):
    try:
        return wait_time_agent.process(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/deterioration", response_model=DeteriorationResponse)
async def deterioration_detection(request: DeteriorationRequest):
    try:
        return deterioration_agent.process(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/training/train-rl")
async def train_agent_rl(agent_id: str, num_episodes: int = 100, learning_rate: float = 0.001, num_epochs: int = 10):
    """Train an agent using Reinforcement Learning."""
    try:
        trainer = get_trainer()
        traces = trainer.collect_traces(agent_id, num_episodes)
        metrics = trainer.train_with_rl(agent_id, traces, learning_rate, num_epochs)
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/training/train-apo")
async def train_agent_apo(agent_id: str, num_episodes: int = 100, learning_rate: float = 0.001, num_epochs: int = 10):
    """Train an agent using Agent Policy Optimization (APO)."""
    try:
        trainer = get_trainer()
        traces = trainer.collect_traces(agent_id, num_episodes)
        metrics = trainer.train_with_apo(agent_id, traces, learning_rate, num_epochs)
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/training/evaluate/{agent_id}")
async def evaluate_agent(agent_id: str):
    """Evaluate a trained agent."""
    try:
        trainer = get_trainer()
        metrics = trainer.evaluate_agent(agent_id)
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/training/emit-trace")
async def emit_trace(agent_id: str, trace_data: dict):
    """Emit a training trace for an agent (agl.emit_xxx() equivalent)."""
    try:
        trainer = get_trainer()
        trace_id = trainer.emit_trace(agent_id, trace_data)
        return {"status": "success", "trace_id": trace_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
