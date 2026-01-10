#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : schemas.py
@Desc    : Pydantic schemas for Document Versioning
"""
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class DocumentVersion(BaseModel):
    """A versioned snapshot of a document"""
    document_id: str           # "prd", "design", "main.py"
    document_type: str = ""    # "prd", "design", "code"
    version: int               # 1, 2, 3...
    content: Union[str, Dict[str, Any]]  # Full snapshot
    content_hash: str = ""     # For quick comparison
    changed_by: str = "System" # "Alice", "Client"
    change_reason: str = ""    # "Client requested feature X"
    timestamp: datetime = Field(default_factory=datetime.now)
    changes_summary: List[str] = Field(default_factory=list)  # Summary of changes
    parent_version: Optional[int] = None  # Previous version
    locked: bool = False       # If true, cannot be modified
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ChangeEntry(BaseModel):
    """A single change in the audit log"""
    id: str = Field(default_factory=lambda: f"chg_{uuid.uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=datetime.now)
    document_id: str
    document_type: str
    version: int
    changed_by: str
    change_reason: str = ""
    changes_summary: str = ""
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class VersionHistory(BaseModel):
    """Complete version history for a document"""
    document_id: str
    document_type: str
    current_version: int = 0
    versions: List[int] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DiffResult(BaseModel):
    """Result of comparing two versions"""
    document_id: str
    v1: int
    v2: int
    added: List[str] = Field(default_factory=list)
    removed: List[str] = Field(default_factory=list)
    modified: List[Dict[str, Any]] = Field(default_factory=list)
    is_json_diff: bool = False
    raw_diff: str = ""  # For text diffs


# API Request/Response schemas

class VersionListResponse(BaseModel):
    """Response with version list"""
    document_id: str
    versions: List[int]
    current: int
    total: int


class VersionDetailResponse(BaseModel):
    """Response with version details"""
    version: int
    content: Union[str, Dict]
    changed_by: str
    change_reason: str
    timestamp: str
    changes_summary: List[str]


class RollbackRequest(BaseModel):
    """Request to rollback"""
    version: int
    reason: str = "Rollback requested"


class RollbackResponse(BaseModel):
    """Response after rollback"""
    rolled_back: bool
    from_version: int
    to_version: int
    new_current: int


class HistoryResponse(BaseModel):
    """Response with project history"""
    timeline: List[ChangeEntry]
    total_changes: int
