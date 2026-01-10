#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : fix_coordinator.py
@Desc    : Route bugs to agents and coordinate fix workflow
"""
import asyncio
from typing import Optional, Dict
from metagpt.logs import logger
from metagpt.testing.schemas import Bug, BugStatus, BugPriority
from metagpt.testing.bug_tracker import bug_tracker
from metagpt.testing.bug_analyzer import BugAnalyzer


class FixCoordinator:
    """Coordinate bug fixing between agents"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FixCoordinator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._analyzer = BugAnalyzer()
        self._fix_attempts: Dict[str, int] = {}  # bug_id -> retry count
        self._max_retries = 3
        self._initialized = True
    
    async def process_new_bug(self, project_id: str, bug: Bug) -> Bug:
        """
        Process a new bug: classify, prioritize, assign, create.
        """
        # 1. Classify severity using LLM
        bug.severity = await self._analyzer.classify_severity(bug)
        
        # 2. Determine priority
        bug.priority = self._analyzer.determine_priority(bug.severity)
        
        # 3. Auto-assign to appropriate agent
        bug.assigned_to = self._analyzer.determine_assignee(bug)
        bug.status = BugStatus.ASSIGNED
        
        # 4. Create in tracker
        await bug_tracker.create(project_id, bug)
        
        # 5. Notify agent via collaboration layer
        await self._notify_agent(project_id, bug)
        
        logger.info(f"Bug {bug.id} processed: {bug.severity.value}/{bug.priority.value} -> {bug.assigned_to}")
        return bug
    
    async def _notify_agent(self, project_id: str, bug: Bug):
        """Notify assigned agent about the bug"""
        try:
            from metagpt.collaboration.agent_messenger import messenger
            from metagpt.collaboration.schemas import MessageType
            
            priority_emoji = {
                "P0": "🔴",
                "P1": "🟡", 
                "P2": "🟢",
                "P3": "⚪"
            }
            
            await messenger.send_message(
                from_agent="BugTracker",
                to_agent=bug.assigned_to,
                content=f"{priority_emoji.get(bug.priority.value, '')} BUG ASSIGNED: {bug.title}\n"
                        f"ID: {bug.id}\n"
                        f"Severity: {bug.severity.value}\n"
                        f"File: {bug.file_path}\n"
                        f"Error: {bug.error_trace[:200]}",
                message_type=MessageType.NOTIFICATION,
                context={"bug_id": bug.id, "project_id": project_id}
            )
        except Exception as e:
            logger.debug(f"Could not notify agent: {e}")
    
    async def start_fix(self, project_id: str, bug_id: str) -> bool:
        """Mark bug as in-progress"""
        return await bug_tracker.update_status(project_id, bug_id, BugStatus.IN_PROGRESS)
    
    async def complete_fix(
        self,
        project_id: str,
        bug_id: str,
        test_passed: bool,
        files_changed: list = None
    ) -> bool:
        """
        Handle fix completion. If tests pass, mark verified. 
        If tests fail, retry or escalate.
        """
        bug = bug_tracker.get(project_id, bug_id)
        if not bug:
            return False
        
        if test_passed:
            # Fix successful
            await bug_tracker.update_status(project_id, bug_id, BugStatus.VERIFIED)
            self._fix_attempts.pop(bug_id, None)
            logger.info(f"Bug {bug_id} verified fixed!")
            return True
        else:
            # Fix failed
            return await self._handle_failed_fix(project_id, bug)
    
    async def _handle_failed_fix(self, project_id: str, bug: Bug) -> bool:
        """Handle failed fix attempt"""
        bug_id = bug.id
        
        # Increment retry count
        self._fix_attempts[bug_id] = self._fix_attempts.get(bug_id, 0) + 1
        retries = self._fix_attempts[bug_id]
        
        bug.retry_count = retries
        
        if retries >= self._max_retries:
            # Escalate - max retries reached
            logger.warning(f"Bug {bug_id} fix failed {retries} times, escalating")
            await self._escalate_bug(project_id, bug)
            return False
        
        # Retry - assign back
        await bug_tracker.update_status(
            project_id, bug_id, BugStatus.ASSIGNED,
            notes=f"Fix attempt {retries} failed, retrying"
        )
        
        # Notify agent to retry
        await self._notify_agent(project_id, bug)
        
        logger.info(f"Bug {bug_id} retry {retries}/{self._max_retries}")
        return False
    
    async def _escalate_bug(self, project_id: str, bug: Bug):
        """Escalate bug that couldn't be fixed"""
        # Notify Alice (PM) about the escalation
        try:
            from metagpt.collaboration.agent_messenger import messenger
            from metagpt.collaboration.schemas import MessageType
            
            await messenger.send_message(
                from_agent="BugTracker",
                to_agent="Alice",
                content=f"🚨 ESCALATION: Bug {bug.id} failed to fix after {self._max_retries} attempts.\n"
                        f"Title: {bug.title}\n"
                        f"Assigned to: {bug.assigned_to}\n"
                        f"Please review and reassign or mark as won't fix.",
                message_type=MessageType.APPROVAL_REQUEST,
                requires_response=True,
                context={"bug_id": bug.id, "project_id": project_id}
            )
        except Exception as e:
            logger.debug(f"Could not escalate bug: {e}")
    
    def get_retry_count(self, bug_id: str) -> int:
        """Get current retry count for a bug"""
        return self._fix_attempts.get(bug_id, 0)


# Global singleton
fix_coordinator = FixCoordinator()
