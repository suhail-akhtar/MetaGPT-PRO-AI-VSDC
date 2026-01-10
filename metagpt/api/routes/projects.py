#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : projects.py
@Desc    : API routes for Project Management (Global)
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.config2 import config
from typing import List
from pydantic import BaseModel
import os

router = APIRouter()

class ProjectInfo(BaseModel):
    id: str
    name: str
    description: str = ""
    status: str = "active"
    progress: int = 0
    progress: int = 0
    updatedAt: str = ""
    agents: List[str] = ["Alice", "Bob", "Alex", "Eve"] # Default agents

def get_workspace_root() -> Path:
    return Path(config.workspace.path) if config.workspace.path else DEFAULT_WORKSPACE_ROOT

@router.get("", response_model=List[ProjectInfo])
async def list_projects():
    """List all projects in the workspace"""
    root = get_workspace_root()
    if not root.exists():
        return []
    
    projects = []
    
    # Check if there is a specific 'projects' subdirectory (common in this repo)
    scan_dir = root / "projects"
    if not scan_dir.exists():
        scan_dir = root
        
    if not scan_dir.exists():
        return []

    # Iterate through directories
    for item in scan_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Skip 'conversations' if we are scanning root
            if scan_dir == root and item.name == 'conversations':
               continue
               
            projects.append(ProjectInfo(
                id=item.name,
                name=item.name.replace('_', ' ').replace('-', ' ').title(),
                description=f"Project {item.name}",
                status="active",
                progress=0,
                updatedAt=str(item.stat().st_mtime)
            ))
            
    return projects
