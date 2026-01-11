#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : project.py
@Desc    : API routes for Sprint/Backlog System
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
from metagpt.project.board_tracker import board_tracker
from metagpt.project.backlog_manager import BacklogManager
from metagpt.project.schemas import (
    TaskStatus,
    TaskMoveRequest,
    TaskMoveResponse,
    SprintResponse,
    BacklogResponse,
    BoardResponse,
    ProjectMetrics,
    Task,
)
from metagpt.logs import logger

router = APIRouter()

# Cache backlog managers per project
_backlog_managers: dict[str, BacklogManager] = {}


def _get_backlog_manager(project_id: str) -> BacklogManager:
    """Get or create BacklogManager for a project"""
    if project_id not in _backlog_managers:
        _backlog_managers[project_id] = BacklogManager(project_id)
    return _backlog_managers[project_id]


@router.get("/{project_id}/sprints")
async def get_sprints(project_id: str):
    """Get all sprints for a project"""
    try:
        manager = _get_backlog_manager(project_id)
        sprints = await manager.load_sprints()
        current = await manager.get_current_sprint()
        
        return {
            "sprints": [s.model_dump() for s in sprints],
            "current_sprint": current,
            "total_sprints": len(sprints)
        }
    except Exception as e:
        logger.exception(f"Failed to get sprints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/sprint/{sprint_num}")
async def get_sprint(project_id: str, sprint_num: int):
    """Get a specific sprint with task details"""
    try:
        manager = _get_backlog_manager(project_id)
        sprints = await manager.load_sprints()
        
        sprint = next((s for s in sprints if s.number == sprint_num), None)
        if not sprint:
            raise HTTPException(status_code=404, detail=f"Sprint {sprint_num} not found")
        
        # Load backlog to get task details
        backlog = await manager.load()
        tasks = []
        if backlog:
            for task_id in sprint.tasks:
                if task_id in backlog.tasks:
                    tasks.append(backlog.tasks[task_id])
        
        return SprintResponse(
            sprint_num=sprint.number,
            name=sprint.name,
            tasks=tasks,
            progress=sprint.progress_percent,
            goals=sprint.goals
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/backlog")
async def get_backlog(project_id: str):
    """Get the full project backlog"""
    try:
        manager = _get_backlog_manager(project_id)
        backlog = await manager.load()
        
        if not backlog:
            raise HTTPException(status_code=404, detail="Backlog not found")
        
        return BacklogResponse(
            stories=list(backlog.stories.values()),
            total_points=backlog.total_points,
            priority_order=backlog.priority_order
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get backlog: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/board")
async def get_board(project_id: str):
    """Get the current Kanban board state"""
    try:
        board = board_tracker.get_board(project_id)
        tasks = board_tracker.get_tasks(project_id)
        
        if not board:
            # Try loading from disk
            board = await board_tracker.load_board(project_id)
            if not board:
                raise HTTPException(status_code=404, detail="Board not found")
        
        def get_tasks_for_column(task_ids: List[str]) -> List[Task]:
            return [tasks[tid] for tid in task_ids if tid in tasks]
        
        return BoardResponse(
            todo=get_tasks_for_column(board.todo),
            in_progress=get_tasks_for_column(board.in_progress),
            review=get_tasks_for_column(board.review),
            testing=get_tasks_for_column(board.testing),
            done=get_tasks_for_column(board.done),
            blocked=get_tasks_for_column(board.blocked)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get board: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/task/move", response_model=TaskMoveResponse)
async def move_task(project_id: str, req: TaskMoveRequest):
    """Move a task to a new status"""
    try:
        success = await board_tracker.move_task(
            project_id=project_id,
            task_id=req.task_id,
            new_status=req.new_status
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Task or board not found")
        
        # Also update in backlog
        manager = _get_backlog_manager(project_id)
        await manager.update_task_status(req.task_id, req.new_status)
        
        return TaskMoveResponse(
            updated=True,
            task_id=req.task_id,
            new_status=req.new_status.value,
            message=f"Task moved to {req.new_status.value}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to move task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/metrics", response_model=ProjectMetrics)
async def get_metrics(project_id: str):
    """Get project progress metrics"""
    try:
        metrics = board_tracker.get_metrics(project_id)
        
        # Enrich with sprint info
        manager = _get_backlog_manager(project_id)
        sprints = await manager.load_sprints()
        current = await manager.get_current_sprint()
        
        metrics.current_sprint = current
        metrics.total_sprints = len(sprints)
        
        return metrics
    except Exception as e:
        logger.exception(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/status")
async def get_project_status(project_id: str):
    """Get real-time execution status"""
    from metagpt.api.services.project_runner import project_runner
    is_running = project_runner.is_running(project_id)
    
    # Check for approval required state
    approval_required = False
    if project_id in project_runner._teams:
        env = project_runner._teams[project_id].env
        if hasattr(env, 'approval_required'):
            approval_required = env.approval_required

    return {
        "project_id": project_id,
        "is_running": is_running,
        "approval_required": approval_required,
        "status": "paused" if approval_required else ("running" if is_running else "idle")
    }

@router.get("/{project_id}/details")
async def get_project_details(project_id: str):
    """Get project metadata (initial requirements)"""
    from metagpt.api.services.project_runner import project_runner
    
    # Use the new load method to ensure we check disk
    metadata = project_runner._load_metadata(project_id)
    return {
        "project_id": project_id,
        "name": metadata.get("name", f"Project {project_id}"), # todo: store real name
        "description": metadata.get("initial_requirements", "No requirements found"),
        "created_at": "Recently", # todo: track time
    }

@router.get("/{project_id}/agents")
async def get_project_agents(project_id: str):
    """Get active agents for the project"""
    from metagpt.api.services.project_runner import project_runner
    
    if project_id not in project_runner._teams:
        return {"agents": []}
        
    env = project_runner._teams[project_id].env
    roles = env.get_roles() # dict of role_profile -> Role
    
    agent_list = []
    for profile, role in roles.items():
        agent_list.append({
            "name": role.name,
            "role": profile, # profile is like "Alice(Product Manager)" usually, need to check
            "status": "active", # simplified
            "currentTask": role.todo.content if role.todo else "Idle",
            "color": "blue" # default
        })
        
    return {"agents": agent_list}

@router.get("/{project_id}/activity")
async def get_project_activity(project_id: str):
    """Get project activity history"""
    from metagpt.api.services.project_runner import project_runner
    
    if project_id not in project_runner._teams:
        return {"activity": []}
        
    env = project_runner._teams[project_id].env
    # history is a generic list of Messages
    # We want to format this for the UI
    
    # Access private _history if necessary or public accessor
    msgs = env.history # history is string usually? No it's CompositeEnv history?
    # Environment.history is usually a string concatenation in basic MetaGPT, 
    # but let's check base_env.py. It might be a list.
    
    # Safely try to get messages
    activity = []
    
    # In base_env.py, self.history = "" (string) usually?
    # Let's check how we can get structured messages.
    # The `ProjectEnvironment` inherits from Environment.
    # We might need to inspect the `repo.docs.msg` or similar?
    
    # For now, let's assume we can get recent messages from the memory of roles?
    # Or better, the board_tracker logs them?
    
    # Let's leave this simple for now and just return what we can
    return {"activity": []} # detailed log implementation needed later


@router.get("/{project_id}/files")
async def get_project_files(project_id: str, path: str = ""):
    """Get project file tree"""
    from metagpt.const import DEFAULT_WORKSPACE_ROOT
    
    # Path is relative to project root
    project_root = DEFAULT_WORKSPACE_ROOT / "projects" / project_id
    target = project_root / path
    
    if not target.exists():
         # If project dir doesn't exist yet, return empty
         return {"path": path, "items": []}
    
    items = []
    for item in target.iterdir():
        items.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size": item.stat().st_size if item.is_file() else 0
        })
    return {"path": path, "items": items}

@router.get("/{project_id}/artifacts")
async def get_project_artifacts(project_id: str):
    """Get key project artifacts"""
    from metagpt.const import DEFAULT_WORKSPACE_ROOT
    
    project_root = DEFAULT_WORKSPACE_ROOT / "projects" / project_id
    artifacts = []
    
    # Common artifacts to look for
    common_files = ["docs/prd.md", "docs/system_design.md", "docs/api_spec_and_tasks.md", "resources/competitive_analysis.md"]
    
    for relative_path in common_files:
        f = project_root / relative_path
        if f.exists():
            artifacts.append({
                "name": f.name,
                "path": str(relative_path), # Used for fetching content
                "type": "document",
                "size": f.stat().st_size
            })
            
    return {"artifacts": artifacts}

@router.post("/{project_id}/resume")
async def resume_project(project_id: str):
    from metagpt.api.services.project_runner import project_runner
    try:
        await project_runner.resume_project(project_id)
        return {"status": "resumed", "project_id": project_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to resume project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/restart")
async def restart_project(project_id: str):
    """Restart project (archive workspace, clear memory, rerun init requirements)"""
    from metagpt.api.services.project_runner import project_runner
    
    # 1. Get initial requirements
    metadata = project_runner._load_metadata(project_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Project metadata not found (active session required for restart)")

    requirements = metadata.get("initial_requirements", "")
    
    try:
        # 2. Reset (Stop + Archive)
        await project_runner.reset_project(project_id)
        
        # 3. Run again
        await project_runner.run_project(project_id, requirements)
        
        return {"status": "restarted", "project_id": project_id}
    except Exception as e:
        logger.exception(f"Failed to restart project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete project and all resources"""
    from metagpt.api.services.project_runner import project_runner
    try:
        await project_runner.delete_project(project_id)
        return {"status": "deleted", "project_id": project_id}
    except Exception as e:
        logger.exception(f"Failed to delete project: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.websocket("/{project_id}/board/stream")
async def board_websocket(websocket: WebSocket, project_id: str):
    """WebSocket for real-time board updates"""
    await websocket.accept()
    board_tracker.add_websocket(project_id, websocket)
    
    try:
        # Send initial state
        board = board_tracker.get_board(project_id)
        if board:
            await websocket.send_json({
                "type": "initial_state",
                "board": board.model_dump()
            })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle any client commands if needed
    except WebSocketDisconnect:
        board_tracker.remove_websocket(project_id, websocket)
    except Exception:
        board_tracker.remove_websocket(project_id, websocket)
