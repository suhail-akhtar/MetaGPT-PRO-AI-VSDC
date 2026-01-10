#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : versions.py
@Desc    : API routes for Document Versioning
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from metagpt.versioning.version_manager import version_manager
from metagpt.versioning.diff_generator import DiffGenerator
from metagpt.versioning.rollback_handler import RollbackHandler
from metagpt.versioning.schemas import (
    VersionListResponse, VersionDetailResponse,
    RollbackRequest, RollbackResponse, HistoryResponse
)
from metagpt.logs import logger

router = APIRouter()
diff_generator = DiffGenerator()
rollback_handler = RollbackHandler()


@router.get("/{project_id}/document/{doc_type}/versions", response_model=VersionListResponse)
async def get_versions(project_id: str, doc_type: str, doc_id: str = Query(default="default")):
    """Get list of all versions for a document"""
    try:
        history = await version_manager.get_versions_list(project_id, doc_id, doc_type)
        
        return VersionListResponse(
            document_id=doc_id,
            versions=list(reversed(history.versions)),  # Newest first
            current=history.current_version,
            total=len(history.versions)
        )
    except Exception as e:
        logger.exception(f"Failed to get versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/document/{doc_type}/version/{version_num}")
async def get_version(
    project_id: str,
    doc_type: str,
    version_num: int,
    doc_id: str = Query(default="default")
):
    """Get a specific version of a document"""
    version = await version_manager.get_version(project_id, doc_id, version_num, doc_type)
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return VersionDetailResponse(
        version=version.version,
        content=version.content,
        changed_by=version.changed_by,
        change_reason=version.change_reason,
        timestamp=version.timestamp.isoformat(),
        changes_summary=version.changes_summary
    )


@router.get("/{project_id}/document/{doc_type}/diff")
async def get_diff(
    project_id: str,
    doc_type: str,
    v1: int = Query(..., description="First version"),
    v2: int = Query(..., description="Second version"),
    doc_id: str = Query(default="default")
):
    """Compare two versions of a document"""
    version1 = await version_manager.get_version(project_id, doc_id, v1, doc_type)
    version2 = await version_manager.get_version(project_id, doc_id, v2, doc_type)
    
    if not version1:
        raise HTTPException(status_code=404, detail=f"Version {v1} not found")
    if not version2:
        raise HTTPException(status_code=404, detail=f"Version {v2} not found")
    
    diff = diff_generator.compare(version1, version2)
    summary = diff_generator.generate_summary(diff)
    
    return {
        "document_id": doc_id,
        "v1": v1,
        "v2": v2,
        "summary": summary,
        "added": diff.added,
        "removed": diff.removed,
        "modified": diff.modified,
        "is_json_diff": diff.is_json_diff,
        "raw_diff": diff.raw_diff if not diff.is_json_diff else None
    }


@router.post("/{project_id}/document/{doc_type}/rollback", response_model=RollbackResponse)
async def rollback_version(
    project_id: str,
    doc_type: str,
    req: RollbackRequest,
    doc_id: str = Query(default="default")
):
    """Rollback to a previous version"""
    # Check current version
    history = await version_manager.get_versions_list(project_id, doc_id, doc_type)
    current = history.current_version
    
    if req.version >= current:
        raise HTTPException(status_code=400, detail="Can only rollback to earlier versions")
    
    if not await rollback_handler.can_rollback(project_id, doc_id, req.version):
        raise HTTPException(status_code=400, detail="Cannot rollback to this version")
    
    success, new_version = await rollback_handler.rollback(
        project_id=project_id,
        document_id=doc_id,
        target_version=req.version,
        reason=req.reason,
        rolled_back_by="Client"
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Rollback failed")
    
    return RollbackResponse(
        rolled_back=True,
        from_version=current,
        to_version=req.version,
        new_current=new_version
    )


@router.get("/{project_id}/history", response_model=HistoryResponse)
async def get_project_history(project_id: str, limit: int = 100):
    """Get project-wide change history"""
    entries = version_manager.get_audit_log(project_id, limit)
    
    return HistoryResponse(
        timeline=entries,
        total_changes=len(entries)
    )


@router.post("/{project_id}/document/{doc_type}/snapshot")
async def create_snapshot(
    project_id: str,
    doc_type: str,
    doc_id: str = Query(default="default"),
    content: str = "",
    changed_by: str = "Client",
    reason: str = ""
):
    """Manually create a version snapshot"""
    try:
        # Try to parse as JSON
        try:
            parsed_content = __import__('json').loads(content)
        except:
            parsed_content = content
        
        version = await version_manager.snapshot(
            project_id=project_id,
            document_id=doc_id,
            document_type=doc_type,
            content=parsed_content,
            changed_by=changed_by,
            change_reason=reason
        )
        
        return {
            "version": version.version,
            "document_id": doc_id,
            "document_type": doc_type,
            "timestamp": version.timestamp.isoformat()
        }
    except Exception as e:
        logger.exception(f"Failed to create snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
