from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.scheduler import scheduler
from app.agents.research_agent import ResearchAgent
from app.agents.script_agent import MalayalamScriptAgent
from app.database import get_db_connection

router = APIRouter(prefix="/workflow", tags=["Workflow Engine"])

class KillswitchRequest(BaseModel):
    active: bool

class ProduceRequest(BaseModel):
    script_id: str

@router.post("/run-cycle")
def run_autonomous_cycle(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Manually triggers one complete autonomous production cycle."""
    if scheduler.is_killswitch_active():
        raise HTTPException(status_code=400, detail="Killswitch is currently active. Clear killswitch before running cycle.")
    
    background_tasks.add_task(scheduler.process_autonomous_cycle)
    return {"status": "started", "message": "Autonomous production cycle dispatched in background."}

@router.post("/discover")
def trigger_discovery(limit: int = 3) -> Dict[str, Any]:
    agent = ResearchAgent()
    topics = agent.discover_topics(limit=limit)
    return {"discovered_count": len(topics), "topics": topics}

@router.post("/generate-script")
def trigger_script_generation(topic_id: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Topic not found")

    agent = MalayalamScriptAgent()
    script = agent.generate_script(dict(row))
    return {"status": "success", "script": script}

@router.post("/produce-video")
def trigger_video_production(req: ProduceRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.*, t.mal_title, t.title, t.category, t.format, t.originality_score, t.fact_status, t.fact_confidence
    FROM scripts s
    JOIN topics t ON s.topic_id = t.id
    WHERE s.id = ?
    """, (req.script_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Script not found")

    script_data = dict(row)
    background_tasks.add_task(scheduler.execute_video_production_pipeline, script_data)
    return {"status": "started", "script_id": req.script_id, "message": "Video rendering pipeline started in background."}

@router.post("/scheduler/start")
def start_scheduler() -> Dict[str, Any]:
    scheduler.start()
    return {"status": "running", "autonomous_mode": True}

@router.post("/scheduler/stop")
def stop_scheduler() -> Dict[str, Any]:
    scheduler.stop()
    return {"status": "stopped", "autonomous_mode": False}

@router.post("/killswitch")
def toggle_killswitch(req: KillswitchRequest) -> Dict[str, Any]:
    scheduler.set_killswitch(req.active)
    return {
        "killswitch_active": req.active,
        "message": "EMERGENCY KILLSWITCH ACTIVATED" if req.active else "Killswitch deactivated"
    }
