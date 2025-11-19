
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import time
from .inference import InferenceService
from ..utils.timing import time_execution

app = FastAPI(title="Event Anomaly Detection Service")

# Dependency Injection for Singleton Model
inference_service = None

@app.on_event("startup")
def load_model():
    global inference_service
    inference_service = InferenceService()
    print("Model loaded successfully")

class LogEvent(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    request_id: str = None

class SequenceRequest(BaseModel):
    events: List[Dict[str, Any]]

@app.post("/score_sequence")
@time_execution
async def score_sequence(request: SequenceRequest):
    if not inference_service:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = time.perf_counter()
    
    result = inference_service.score_sequence(request.events)
    
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    result["latency_ms"] = latency_ms
    return result

@app.get("/health")
def health():
    return {"status": "ok"}
