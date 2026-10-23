from pathlib import Path
from threading import RLock
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app.ml import MODELS, LOCK, CATEGORIES, PRIORITIES

ROOT = Path(__file__).resolve().parent
FEEDBACK_PATH = ROOT / "feedback.json"
app = FastAPI(title="Support Ticket Intelligence API", version="1.0.0",
              description="Synthetic-data demo for ticket category and priority prediction.")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
feedback_lock = RLock()

class TicketRequest(BaseModel):
    text: str = Field(min_length=8, max_length=5000)

class FeedbackRequest(BaseModel):
    text: str = Field(min_length=8, max_length=5000)
    predicted_category: Optional[str] = None
    predicted_priority: Optional[str] = None
    correct_category: str
    correct_priority: str
    helpful: bool = True

def read_feedback():
    if not FEEDBACK_PATH.exists():
        return []
    try:
        return json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

def write_feedback(rows):
    FEEDBACK_PATH.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

@app.on_event("startup")
def startup():
    feedback = read_feedback()
    MODELS.train(feedback)

@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "model_ready": MODELS.category_model is not None,
            "feedback_count": len(read_feedback())}

@app.post("/api/predict")
def predict(payload: TicketRequest):
    text = payload.text.strip()
    if len(text) < 8:
        raise HTTPException(status_code=422, detail="Please enter at least 8 characters.")
    return MODELS.predict(text)

@app.get("/api/metrics")
def metrics():
    return MODELS.metrics

@app.get("/api/categories")
def categories():
    return {"categories": CATEGORIES, "priorities": PRIORITIES}

@app.post("/api/feedback")
def feedback(payload: FeedbackRequest):
    if payload.correct_category not in CATEGORIES:
        raise HTTPException(status_code=422, detail="Unknown category.")
    if payload.correct_priority not in PRIORITIES:
        raise HTTPException(status_code=422, detail="Unknown priority.")
    row = payload.model_dump()
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    with feedback_lock:
        rows = read_feedback()
        rows.append(row)
        write_feedback(rows)
    return {"saved": True, "feedback_count": len(rows),
            "message": "Feedback saved. Retraining is available from the admin panel."}

@app.post("/api/retrain")
def retrain():
    rows = read_feedback()
    with LOCK:
        MODELS.train(rows)
    return {"retrained": True, "metrics": MODELS.metrics,
            "message": "Models retrained with synthetic data and submitted feedback."}
