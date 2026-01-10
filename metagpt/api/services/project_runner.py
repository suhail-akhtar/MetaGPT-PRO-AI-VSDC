#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : project_runner.py
@Desc    : Service to manage background execution of MetaGPT projects
"""
import asyncio
from typing import Dict, Optional
from metagpt.logs import logger
from metagpt.team import Team
from metagpt.context import Context
from metagpt.config2 import Config
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.roles import (
    Architect,
    DataAnalyst,
    Engineer2,
    ProductManager,
    TeamLeader,
)

class ProjectRunner:
    """Singleton service to manage project execution"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectRunner, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._running_projects: Dict[str, asyncio.Task] = {}
        self._teams: Dict[str, Team] = {}
        self._initialized = True
    
    async def run_project(self, project_id: str, requirements: str, n_round: int = 5):
        """
        Start running a project with approved requirements.
        
        Args:
            project_id: The project ID (e.g., 'proj_123')
            requirements: The approved requirements text
            n_round: Number of rounds to run
        """
        if project_id in self._running_projects and not self._running_projects[project_id].done():
            logger.warning(f"Project {project_id} is already running")
            return

        # Create task
        task = asyncio.create_task(self._execute_team(project_id, requirements, n_round))
        self._running_projects[project_id] = task
        
        # Cleanup callback
        def cleanup(future):
            if project_id in self._running_projects:
                pass # Keep record but mark done?
        
        task.add_done_callback(cleanup)
        logger.info(f"Started project execution for {project_id}")
    
    async def _execute_team(self, project_id: str, requirements: str, n_round: int):
        """Internal execution logic"""
        try:
            # Create isolated context for this project
            config = Config.default()
            # Ensure workspace path structure: workspace/project_id
            # MetaGPT defaults to creating a folder with project_name under workspace
            # We want strict control, so we set the git repo path essentially
            
            ctx = Context(config=config)
            
            # Initialize Team
            company = Team(context=ctx)
            
            # Hire standard role set
            # Hire updated role set from software_company.py
            company.hire([
                TeamLeader(),
                ProductManager(use_fixed_sop=False),
                Architect(use_fixed_sop=False),
                Engineer2(use_fixed_sop=False),
                DataAnalyst(),
            ])
            
            # Invest
            company.invest(investment=10.0)
            
            # Store reference
            self._teams[project_id] = company
            
            # Initialize empty board state so UI doesn't 404
            from metagpt.project.board_tracker import board_tracker
            await board_tracker.initialize_board(project_id, {})
            
            # Run
            # We use project_id as the idea/requirement input for now if it accepts text
            logger.info(f"Team {project_id} starting run loop")
            await company.run(n_round=n_round, idea=requirements)
            
            logger.info(f"Team {project_id} finished run loop")
            
        except Exception as e:
            logger.exception(f"Error executing project {project_id}: {e}")
            raise

    def is_running(self, project_id: str) -> bool:
        return project_id in self._running_projects and not self._running_projects[project_id].done()

# Global instance
project_runner = ProjectRunner()
