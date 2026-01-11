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
from metagpt.api.services.project_env import ProjectEnvironment
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
        self._project_metadata: Dict[str, dict] = {}
        self._initialized = True
    
    
    def _get_project_path(self, project_id: str):
        from metagpt.const import DEFAULT_WORKSPACE_ROOT
        from pathlib import Path
        return Path(DEFAULT_WORKSPACE_ROOT) / "projects" / project_id

    def _save_metadata(self, project_id: str):
        """Save project metadata to disk"""
        import json
        if project_id not in self._project_metadata:
            return
            
        project_path = self._get_project_path(project_id)
        if not project_path.exists():
            project_path.mkdir(parents=True, exist_ok=True)
            
        try:
            with open(project_path / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(self._project_metadata[project_id], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata for {project_id}: {e}")

    def _load_metadata(self, project_id: str) -> dict:
        """Load metadata from disk if not in memory"""
        if project_id in self._project_metadata:
            return self._project_metadata[project_id]
            
        project_path = self._get_project_path(project_id)
        metadata_file = project_path / "metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._project_metadata[project_id] = data
                    return data
            except Exception as e:
                logger.error(f"Failed to load metadata for {project_id}: {e}")
        
        return {}
    
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
        self._project_metadata[project_id] = {
            "initial_requirements": requirements,
            "status": "active"
        }
        self._save_metadata(project_id)
        
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
            
            # Initialize Team with Custom ProjectEnvironment
            env = ProjectEnvironment(project_id=project_id, context=ctx)
            company = Team(context=ctx, env=env)
            
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
            
            # Run loop with pause check
            logger.info(f"Team {project_id} starting run loop. Rounds: {remaining_rounds}")
            logger.info(f"Initial requirements length: {len(requirements)}")
            
            while remaining_rounds > 0:
                logger.info(f"[{project_id}] Round {n_round - remaining_rounds + 1}/{n_round}. Items in env history: {len(env.history)}")
                
                if env.approval_required:
                    logger.info(f"[{project_id}] PAUSED for approval.")
                    break
                if env.approval_required:
                    logger.info(f"[{project_id}] PAUSED for approval.")
                    break
                
                await company.run(n_round=1, idea=requirements)

                
                # Check if we are idle after run (which means no agents did anything)
                if env.is_idle:
                    logger.info(f"[{project_id}] Env is IDLE after round. Breaking.")
                    break
                    
                remaining_rounds -= 1
                requirements = "" # Clear idea for subsequent rounds
            
            if not env.approval_required:
                logger.info(f"Team {project_id} finished run loop naturally")
            
        except Exception as e:
            logger.exception(f"Error executing project {project_id}: {e}")
            raise

    async def resume_project(self, project_id: str, n_round: int = 5):
        """Resume a paused project"""
        if project_id not in self._teams:
            raise ValueError(f"Project {project_id} not found in memory")
            
        company = self._teams[project_id]
        if hasattr(company.env, 'approval_required'):
            company.env.approval_required = False
            
        logger.info(f"Resuming project {project_id}")
        
        # Re-enter execution loop (as a new task)
        # We need to ensure we don't have double-running tasks
        if self.is_running(project_id):
             logger.warning(f"Project {project_id} is already running")
             return

        # Start new background task for remaining rounds
        task = asyncio.create_task(self._execute_existing_team(project_id, n_round))
        self._running_projects[project_id] = task
        
    async def _execute_existing_team(self, project_id: str, n_round: int):
        """Execute an existing team instance"""
        try:
            company = self._teams[project_id]
            env = company.env
            
            remaining_rounds = n_round
            while remaining_rounds > 0:
                if getattr(env, 'approval_required', False):
                    logger.info(f"Project {project_id} paused for approval.")
                    break
                
                await company.run(n_round=1)
                remaining_rounds -= 1
                
        except Exception as e:
            logger.exception(f"Error resuming project {project_id}: {e}")

    async def stop_project(self, project_id: str):
        """Stop a running project"""
        if self.is_running(project_id):
            task = self._running_projects[project_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Project {project_id} stopped")
            del self._running_projects[project_id]

    async def delete_project(self, project_id: str):
        """Delete a project and its workspace"""
        # Stop first
        await self.stop_project(project_id)
        
        # Remove from memory
        if project_id in self._teams:
            del self._teams[project_id]
        if project_id in self._project_metadata:
            del self._project_metadata[project_id]
            
        # Delete files
        import shutil
        from metagpt.const import DEFAULT_WORKSPACE_ROOT
        project_path = DEFAULT_WORKSPACE_ROOT / "projects" / project_id
        if project_path.exists():
            shutil.rmtree(project_path)
            logger.info(f"Deleted workspace for {project_id}")

    async def reset_project(self, project_id: str):
        """Reset a project execution (clear memory, keep metadata)"""
         # Stop first
        await self.stop_project(project_id)
        
        # Remove from memory (execution state)
        if project_id in self._teams:
            del self._teams[project_id]
            
        # We KEEP the metadata (requirements) so we can restart with them
        # Optional: Archive old files instead of deleting?
        # For now, let's keep it simple: restart assumes 'run_project' will be called again
        # which overwrites or appends.
        # If we want a clean slate, we should maybe archive the old 'projects/proj_id' folder
        
        from metagpt.const import DEFAULT_WORKSPACE_ROOT
        import shutil
        import time
        
        project_path = DEFAULT_WORKSPACE_ROOT / "projects" / project_id
        if project_path.exists():
            # Archive
            archive_path = DEFAULT_WORKSPACE_ROOT / "projects" / f"{project_id}_archive_{int(time.time())}"
            shutil.move(str(project_path), str(archive_path))
            logger.info(f"Archived {project_id} to {archive_path}")

    def is_running(self, project_id: str) -> bool:
        return project_id in self._running_projects and not self._running_projects[project_id].done()


# Global instance
project_runner = ProjectRunner()
