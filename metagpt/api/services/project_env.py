#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/11
@Author  : MetaGPT-Pro Team
@File    : project_env.py
@Desc    : Custom Environment with hooks for Board and Approval Sync
"""

import json
import re
from typing import Optional

from metagpt.environment.base_env import Environment
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.project.board_tracker import board_tracker, Task, TaskStatus

class ProjectEnvironment(Environment):
    """
    Project-specific environment that:
    1. Listens for PRD generation to create Board Tasks
    2. Listens for Code generation to update Task Status
    3. Pauses execution for generic approvals
    """
    
    project_id: str = ""
    approval_required: bool = False
    
    def __init__(self, project_id: str, **kwargs):
        super().__init__(**kwargs)
        self.project_id = project_id
    
    def publish_message(self, message: Message, peekable: bool = True) -> bool:
        """
        Intercept published messages to update board state
        """
        # 1. Standard publish
        res = super().publish_message(message, peekable)
        
        # 2. Sync with Board / Status
        try:
            self._sync_message(message)
        except Exception as e:
            logger.warning(f"Failed to sync message to board: {e}")
            
        return res

    def _sync_message(self, message: Message):
        """Analyze message content and update board tracker"""
        role = message.role if hasattr(message, 'role') else ""
        content = message.content
        
        if role != "Product Manager": # Reduce noise
             pass
        logger.info(f"[{self.project_id}] Message Published. Role: {role}, Content-Len: {len(content)}")
        
        # Scenario A: Product Manager produced a PRD
        if role == "Product Manager" and "PRD" in content and "User Stories" in content:
            self._handle_prd_generated(content)
        
        # Scenario B: Engineer fixed a bug or wrote code (simplified detection)
        if role == "Engineer" and "Write code" in str(message.cause_by): 
            # This is harder to map 1:1 without more context, skipping for now or strictly looking for file paths
            pass

    def _handle_prd_generated(self, content: str):
        """Parse PRD to extract User Stories and populate Board"""
        logger.info(f"[{self.project_id}] PRD detected! Parsing for board tasks...")
        
        # Simple parsing logic (can be improved with strict JSON usage if available)
        # Assuming markdown or JSON content.
        
        stories = []
        
        # Try to find user stories list
        # Pattern like "## User Stories" followed by "- ..."
        match = re.search(r"## User Stories\s*\n((?:[-*].*\n?)+)", content)
        if match:
            raw_stories = match.group(1).strip().split('\n')
            for s in raw_stories:
                clean_s = s.strip().lstrip('-* ').strip()
                if clean_s:
                    stories.append(clean_s)
        
        if not stories:
            logger.warning("No user stories found in PRD.")
            return

        # Create tasks on Board
        tasks = {}
        import uuid
        for i, story in enumerate(stories):
            t_id = f"task_{uuid.uuid4().hex[:6]}"
            tasks[t_id] = Task(
                id=t_id,
                title=story[:50] + "..." if len(story) > 50 else story,
                description=story,
                status=TaskStatus.TODO,
                assignee="Engineer"
            )
        
        # Initialize (or Update) Board
        # We use a Fire-and-Forget async task here or standard sync if loop allows
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(board_tracker.initialize_board(self.project_id, tasks))
        except Exception as e:
            logger.error(f"Async board update failed: {e}")

        # IMPORTANT: Pause for Approval because PRD is done
        self.approval_required = True
        logger.info(f"[{self.project_id}] Execution paused for PRD approval.")

