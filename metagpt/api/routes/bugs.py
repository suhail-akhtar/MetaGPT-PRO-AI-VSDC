#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : bugs.py
@Desc    : API routes for Bug Tracking
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Optional
from metagpt.testing.bug_tracker import bug_tracker
from metagpt.testing.bug_detector import bug_detector
from metagpt.testing.fix_coordinator import fix_coordinator
from metagpt.testing.schemas import (
    Bug, BugStatus, BugSource,
    BugReportRequest, BugReportResponse,
    BugAssignRequest, BugStatusRequest,
    BugListResponse, BugMetrics
)
from metagpt.logs import logger

router = APIRouter()


@router.get("/{project_id}/bugs", response_model=BugListResponse)
async def get_bugs(project_id: str, status: Optional[str] = None):
    """Get all bugs for a project"""
    try:
        # Load from disk if needed
        await bug_tracker.load_bugs(project_id)
        
        status_filter = None
        if status:
            try:
                status_filter = BugStatus(status)
            except:
                pass
        
        bugs = bug_tracker.get_all(project_id, status_filter)
        open_bugs = bug_tracker.get_open(project_id)
        critical = [b for b in bugs if b.severity.value == "critical"]
        
        return BugListResponse(
            bugs=bugs,
            open_count=len(open_bugs),
            critical_count=len(critical),
            total=len(bugs)
        )
    except Exception as e:
        logger.exception(f"Failed to get bugs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/bug/report", response_model=BugReportResponse)
async def report_bug(project_id: str, req: BugReportRequest):
    """Manually report a bug"""
    try:
        bug = Bug(
            title=req.title,
            description=req.description,
            severity=req.severity,
            file_path=req.file_path,
            error_trace=req.error_trace,
            source=BugSource.MANUAL,
            created_by="Client"
        )
        
        # Process: classify, prioritize, assign
        bug = await fix_coordinator.process_new_bug(project_id, bug)
        
        return BugReportResponse(
            bug_id=bug.id,
            priority=bug.priority.value,
            assigned_to=bug.assigned_to
        )
    except Exception as e:
        logger.exception(f"Failed to report bug: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/bug/{bug_id}")
async def get_bug(project_id: str, bug_id: str):
    """Get bug details with history"""
    bug = bug_tracker.get(project_id, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    history = bug_tracker.get_history(bug_id)
    
    return {
        "bug": bug.model_dump(),
        "history": [h.model_dump() for h in history]
    }


@router.post("/{project_id}/bug/{bug_id}/assign")
async def assign_bug(project_id: str, bug_id: str, req: BugAssignRequest):
    """Assign bug to an agent"""
    success = await bug_tracker.assign(project_id, bug_id, req.agent)
    if not success:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    return {"assigned": True, "agent": req.agent}


@router.patch("/{project_id}/bug/{bug_id}/status")
async def update_bug_status(project_id: str, bug_id: str, req: BugStatusRequest):
    """Update bug status"""
    success = await bug_tracker.update_status(project_id, bug_id, req.status, req.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    return {"updated": True, "status": req.status.value}


@router.get("/{project_id}/metrics/bugs", response_model=BugMetrics)
async def get_bug_metrics(project_id: str):
    """Get bug statistics"""
    await bug_tracker.load_bugs(project_id)
    return bug_tracker.get_metrics(project_id)


@router.post("/{project_id}/bug/detect")
async def detect_bugs_from_output(project_id: str, test_output: str):
    """Parse test output and create bugs"""
    bugs = bug_detector.extract_bugs(test_output, project_id)
    
    created = []
    for bug in bugs:
        processed = await fix_coordinator.process_new_bug(project_id, bug)
        created.append(processed.id)
    
    return {
        "detected": len(bugs),
        "bug_ids": created
    }


@router.websocket("/{project_id}/bugs/stream")
async def bugs_websocket(websocket: WebSocket, project_id: str):
    """WebSocket for real-time bug events"""
    await websocket.accept()
    bug_tracker.add_websocket(project_id, websocket)
    
    try:
        # Send initial state
        await bug_tracker.load_bugs(project_id)
        bugs = bug_tracker.get_all(project_id)
        open_bugs = bug_tracker.get_open(project_id)
        
        await websocket.send_json({
            "type": "initial_state",
            "total_bugs": len(bugs),
            "open_bugs": len(open_bugs)
        })
        
        # Keep alive
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        bug_tracker.remove_websocket(project_id, websocket)
    except Exception:
        bug_tracker.remove_websocket(project_id, websocket)
