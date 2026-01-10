#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : schemas.py
@Desc    : Pydantic schemas for Bug Tracking System
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class BugSeverity(str, Enum):
    """Bug severity levels"""
    CRITICAL = "critical"  # Crash, data loss, security
    HIGH = "high"          # Feature broken
    MEDIUM = "medium"      # Minor issue, workaround exists
    LOW = "low"            # UI glitch, typo


class BugPriority(str, Enum):
    """Bug priority for scheduling"""
    P0 = "P0"  # Interrupt current work
    P1 = "P1"  # Add to current sprint
    P2 = "P2"  # Next sprint
    P3 = "P3"  # Backlog


class BugStatus(str, Enum):
    """Bug lifecycle status"""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    VERIFIED = "verified"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"


class BugSource(str, Enum):
    """How the bug was found"""
    AUTO_TEST = "auto_test"
    MANUAL = "manual"
    CODE_REVIEW = "code_review"
    CLIENT = "client"


class Bug(BaseModel):
    """A bug/issue ticket"""
    id: str = Field(default_factory=lambda: f"BUG-{uuid.uuid4().hex[:6].upper()}")
    title: str
    description: str = ""
    severity: BugSeverity = BugSeverity.MEDIUM
    priority: BugPriority = BugPriority.P2
    status: BugStatus = BugStatus.OPEN
    source: BugSource = BugSource.MANUAL
    
    # Context
    file_path: str = ""
    error_trace: str = ""
    test_name: str = ""
    line_number: int = 0
    
    # Assignment
    assigned_to: Optional[str] = None  # "Alex"
    created_by: str = "System"
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    fixed_at: Optional[datetime] = None
    sprint: int = 0
    related_task: Optional[str] = None
    
    # Resolution
    fix_commit: str = ""
    verification_notes: str = ""
    retry_count: int = 0
    max_retries: int = 3
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BugFix(BaseModel):
    """Record of a bug fix"""
    bug_id: str
    files_changed: List[str] = Field(default_factory=list)
    test_added: bool = False
    verified_by: str = ""
    fix_description: str = ""
    fixed_at: datetime = Field(default_factory=datetime.now)


class BugHistory(BaseModel):
    """History entry for bug changes"""
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str  # "created", "assigned", "status_change", "fixed"
    old_value: str = ""
    new_value: str = ""
    by: str = "System"


# API Request/Response schemas

class BugReportRequest(BaseModel):
    """Request to create a bug manually"""
    title: str
    description: str = ""
    severity: BugSeverity = BugSeverity.MEDIUM
    file_path: str = ""
    error_trace: str = ""


class BugReportResponse(BaseModel):
    """Response after creating bug"""
    bug_id: str
    priority: str
    assigned_to: Optional[str]


class BugAssignRequest(BaseModel):
    """Request to assign bug"""
    agent: str


class BugStatusRequest(BaseModel):
    """Request to update bug status"""
    status: BugStatus
    notes: str = ""


class BugListResponse(BaseModel):
    """Response with bug list"""
    bugs: List[Bug]
    open_count: int
    critical_count: int
    total: int


class BugMetrics(BaseModel):
    """Bug statistics"""
    total_bugs: int = 0
    open: int = 0
    fixed: int = 0
    avg_fix_time_hours: float = 0.0
    by_severity: Dict[str, int] = Field(default_factory=dict)
    by_sprint: Dict[str, int] = Field(default_factory=dict)
