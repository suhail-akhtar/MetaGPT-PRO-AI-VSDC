#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Direct test of project management initialization"""
import asyncio
from metagpt.project.task_breakdown import TaskBreakdownGenerator
from metagpt.project.sprint_planner import SprintPlanner
from metagpt.project.backlog_manager import BacklogManager
from metagpt.project.board_tracker import board_tracker

async def test_project_management():
    req = "Build a simple calculator with +, -, *, / operations"
    project_id = "test_project"
    
    print("1. Generating task breakdown...")
    generator = TaskBreakdownGenerator()
    breakdown = await generator.generate(req)
    print(f"   Epics: {len(breakdown['epics'])}")
    print(f"   Stories: {len(breakdown['stories'])}")
    print(f"   Tasks: {len(breakdown['tasks'])}")
    
    print("\n2. Initializing backlog...")
    manager = BacklogManager(project_id)
    await manager.initialize(breakdown['epics'], breakdown['stories'], breakdown['tasks'])
    print("   Backlog saved")
    
    print("\n3. Creating sprints...")
    planner = SprintPlanner()
    sprints = planner.create_sprints(breakdown['tasks'], breakdown['stories'])
    await manager.save_sprints(sprints)
    print(f"   Sprints: {len(sprints)}")
    
    print("\n4. Initializing board...")
    await board_tracker.initialize_board(project_id, breakdown['tasks'])
    print("   Board initialized")
    
    print("\n5. Checking files...")
    import os
    from metagpt.const import DEFAULT_WORKSPACE_ROOT
    project_dir = DEFAULT_WORKSPACE_ROOT / "projects" / project_id
    print(f"   Project dir: {project_dir}")
    if project_dir.exists():
        for f in project_dir.iterdir():
            print(f"   - {f.name}")
    else:
        print("   Directory does not exist!")
    
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(test_project_management())
