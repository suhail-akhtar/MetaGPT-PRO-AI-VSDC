#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : bug_tracker.py
@Desc    : Manage bug lifecycle and persistence
"""
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from fastapi import WebSocket
from metagpt.logs import logger
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.testing.schemas import (
    Bug, BugStatus, BugPriority, BugSeverity, BugHistory, BugMetrics
)


class BugTracker:
    """Singleton bug tracker with lifecycle management"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BugTracker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._bugs: Dict[str, Dict[str, Bug]] = {}  # project_id -> bug_id -> Bug
        self._history: Dict[str, List[BugHistory]] = {}  # bug_id -> history
        self._websockets: Dict[str, Set[WebSocket]] = {}  # project_id -> websockets
        self._initialized = True
    
    def _get_storage_path(self, project_id: str) -> Path:
        path = DEFAULT_WORKSPACE_ROOT / "projects" / project_id / "bugs"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    async def create(self, project_id: str, bug: Bug) -> Bug:
        """Create a new bug"""
        if project_id not in self._bugs:
            self._bugs[project_id] = {}
        
        # Auto-assign priority based on severity
        if bug.priority == BugPriority.P2:  # Default
            bug.priority = self._severity_to_priority(bug.severity)
        
        self._bugs[project_id][bug.id] = bug
        self._history[bug.id] = [BugHistory(action="created", new_value=bug.status.value)]
        
        # Persist
        await self._save_bug(project_id, bug)
        
        # Broadcast
        await self._broadcast(project_id, {
            "type": "bug_created",
            "bug_id": bug.id,
            "title": bug.title,
            "severity": bug.severity.value,
            "priority": bug.priority.value
        })
        
        logger.info(f"Bug created: {bug.id} - {bug.title} [{bug.severity.value}]")
        return bug
    
    def _severity_to_priority(self, severity: BugSeverity) -> BugPriority:
        """Map severity to priority"""
        mapping = {
            BugSeverity.CRITICAL: BugPriority.P0,
            BugSeverity.HIGH: BugPriority.P1,
            BugSeverity.MEDIUM: BugPriority.P2,
            BugSeverity.LOW: BugPriority.P3
        }
        return mapping.get(severity, BugPriority.P2)
    
    async def assign(self, project_id: str, bug_id: str, agent: str) -> bool:
        """Assign bug to an agent"""
        bug = self.get(project_id, bug_id)
        if not bug:
            return False
        
        old_assignee = bug.assigned_to or "none"
        bug.assigned_to = agent
        bug.status = BugStatus.ASSIGNED
        bug.updated_at = datetime.now()
        
        self._add_history(bug_id, "assigned", old_assignee, agent)
        await self._save_bug(project_id, bug)
        
        await self._broadcast(project_id, {
            "type": "bug_assigned",
            "bug_id": bug_id,
            "agent": agent
        })
        
        logger.info(f"Bug {bug_id} assigned to {agent}")
        return True
    
    async def update_status(
        self,
        project_id: str,
        bug_id: str,
        status: BugStatus,
        notes: str = ""
    ) -> bool:
        """Update bug status"""
        bug = self.get(project_id, bug_id)
        if not bug:
            return False
        
        old_status = bug.status.value
        bug.status = status
        bug.updated_at = datetime.now()
        
        if status == BugStatus.FIXED:
            bug.fixed_at = datetime.now()
        
        if notes:
            bug.verification_notes = notes
        
        self._add_history(bug_id, "status_change", old_status, status.value)
        await self._save_bug(project_id, bug)
        
        await self._broadcast(project_id, {
            "type": f"bug_{status.value}",
            "bug_id": bug_id,
            "old_status": old_status,
            "new_status": status.value
        })
        
        logger.info(f"Bug {bug_id}: {old_status} -> {status.value}")
        return True
    
    def get(self, project_id: str, bug_id: str) -> Optional[Bug]:
        """Get a bug by ID"""
        if project_id not in self._bugs:
            return None
        return self._bugs[project_id].get(bug_id)
    
    def get_all(self, project_id: str, status: BugStatus = None) -> List[Bug]:
        """Get all bugs for a project"""
        if project_id not in self._bugs:
            return []
        
        bugs = list(self._bugs[project_id].values())
        if status:
            bugs = [b for b in bugs if b.status == status]
        
        return sorted(bugs, key=lambda b: (b.priority.value, b.created_at))
    
    def get_open(self, project_id: str) -> List[Bug]:
        """Get open bugs (not fixed/closed)"""
        all_bugs = self.get_all(project_id)
        return [b for b in all_bugs if b.status not in [BugStatus.CLOSED, BugStatus.VERIFIED, BugStatus.WONT_FIX]]
    
    def get_metrics(self, project_id: str) -> BugMetrics:
        """Calculate bug metrics"""
        bugs = self.get_all(project_id)
        
        if not bugs:
            return BugMetrics()
        
        open_bugs = [b for b in bugs if b.status in [BugStatus.OPEN, BugStatus.ASSIGNED, BugStatus.IN_PROGRESS]]
        fixed_bugs = [b for b in bugs if b.status in [BugStatus.FIXED, BugStatus.VERIFIED, BugStatus.CLOSED]]
        
        # Calculate average fix time
        fix_times = []
        for b in fixed_bugs:
            if b.fixed_at:
                delta = (b.fixed_at - b.created_at).total_seconds() / 3600
                fix_times.append(delta)
        
        avg_fix = sum(fix_times) / len(fix_times) if fix_times else 0
        
        # Count by severity
        by_severity = {}
        for sev in BugSeverity:
            count = len([b for b in bugs if b.severity == sev])
            if count > 0:
                by_severity[sev.value] = count
        
        # Count by sprint
        by_sprint = {}
        for b in bugs:
            sprint_key = f"sprint_{b.sprint}" if b.sprint > 0 else "backlog"
            by_sprint[sprint_key] = by_sprint.get(sprint_key, 0) + 1
        
        return BugMetrics(
            total_bugs=len(bugs),
            open=len(open_bugs),
            fixed=len(fixed_bugs),
            avg_fix_time_hours=round(avg_fix, 2),
            by_severity=by_severity,
            by_sprint=by_sprint
        )
    
    def _add_history(self, bug_id: str, action: str, old_value: str, new_value: str):
        """Add history entry"""
        if bug_id not in self._history:
            self._history[bug_id] = []
        
        self._history[bug_id].append(BugHistory(
            action=action,
            old_value=old_value,
            new_value=new_value
        ))
    
    def get_history(self, bug_id: str) -> List[BugHistory]:
        """Get bug history"""
        return self._history.get(bug_id, [])
    
    async def _save_bug(self, project_id: str, bug: Bug):
        """Persist bug to disk"""
        path = self._get_storage_path(project_id)
        bug_file = path / f"{bug.id}.json"
        
        with open(bug_file, 'w', encoding='utf-8') as f:
            json.dump(bug.model_dump(), f, indent=2, default=str)
    
    async def load_bugs(self, project_id: str):
        """Load bugs from disk"""
        path = self._get_storage_path(project_id)
        
        if project_id not in self._bugs:
            self._bugs[project_id] = {}
        
        for bug_file in path.glob("BUG-*.json"):
            try:
                with open(bug_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                bug = Bug(**data)
                self._bugs[project_id][bug.id] = bug
            except Exception as e:
                logger.warning(f"Failed to load bug {bug_file}: {e}")
    
    # WebSocket management
    def add_websocket(self, project_id: str, ws: WebSocket):
        if project_id not in self._websockets:
            self._websockets[project_id] = set()
        self._websockets[project_id].add(ws)
    
    def remove_websocket(self, project_id: str, ws: WebSocket):
        if project_id in self._websockets:
            self._websockets[project_id].discard(ws)
    
    async def _broadcast(self, project_id: str, message: dict):
        """Broadcast to project WebSockets"""
        if project_id not in self._websockets:
            return
        
        msg_str = json.dumps(message, default=str)
        for ws in list(self._websockets[project_id]):
            try:
                await ws.send_text(msg_str)
            except:
                self._websockets[project_id].discard(ws)


# Global singleton
bug_tracker = BugTracker()
