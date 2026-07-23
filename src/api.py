from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

from src.main import run_pipeline
from src.ingestion.search import resolve_app_ids

log = logging.getLogger("WeeklyPulseAPI")

app = FastAPI(title="Weekly Pulse API")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Weekly Pulse API"}

class AnalyzeRequest(BaseModel):
    app_name: str

@app.post("/api/analyze")
def analyze_app(request: AnalyzeRequest):
    try:
        log.info(f"Resolving IDs for app name: {request.app_name}")
        play_store_id, app_store_id = resolve_app_ids(request.app_name)
        
        # We need at least one ID to proceed, but the pipeline requires both currently.
        # If one is missing, we could pass a dummy value, but resolve_app_ids will 
        # return None if not found. Let's pass empty strings or 'UNKNOWN' if missing,
        # but the pipeline might fail if the fetcher errors out.
        # Actually, let's just pass whatever we got. The fetchers handle bad IDs gracefully 
        # (they just return 0 reviews).
        p_id = play_store_id or "UNKNOWN"
        a_id = app_store_id or "UNKNOWN"
        
        log.info(f"Starting analysis for {p_id} / {a_id}")
        
        # Hardcode count to 50 as requested to simplify the UI
        result = run_pipeline(
            play_store_id=p_id,
            app_store_id=a_id,
            count=50
        )
        
        # Add the resolved name to the result so the frontend can display it
        result["app_name_query"] = request.app_name
        
        return {"status": "success", "data": result}
    except ValueError as e:
        log.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)

