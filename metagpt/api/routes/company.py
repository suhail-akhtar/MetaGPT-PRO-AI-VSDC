from fastapi import APIRouter, HTTPException
from metagpt.api.orchestrator import orchestrator
from metagpt.api.schemas import ProjectRequest, CompanyStatus

router = APIRouter()

@router.post("/hire")
async def hire_team():
    """Initialize or Reset the Virtual Company Team"""
    orchestrator.hire()
    return {"message": "Team has been hired and is ready for work."}

@router.post("/run")
async def run_project(req: ProjectRequest):
    """Submit a new project/requirement to the company"""
    try:
        await orchestrator.start_project(req)
        return {"message": "Project started successfully.", "project": req.project_name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stop")
async def stop_project():
    """Stop the current project execution"""
    await orchestrator.stop()
    return {"message": "Project execution stopped."}

@router.get("/status", response_model=CompanyStatus)
async def get_status():
    """Get the current detailed status of the company"""
    return orchestrator.get_status()

@router.get("/history")
async def get_history():
    """Get the global message history of the company"""
    if not orchestrator.team:
        return []
    # return list of messages
    return [m.model_dump() for m in orchestrator.team.env.history.get()]

@router.get("/plan")
async def get_plan():
    """Get the current project plan (WBS/Tasks)"""
    plan = await orchestrator.get_plan()
    if not plan:
        return {"message": "Plan not available yet or no project running."}
    return plan
