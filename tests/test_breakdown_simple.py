#!/usr/bin/env python
import asyncio
from metagpt.project.task_breakdown import TaskBreakdownGenerator
from metagpt.project.backlog_manager import BacklogManager
from metagpt.project.board_tracker import board_tracker
from pathlib import Path

async def test():
    print("1. Generating breakdown...")
    g = TaskBreakdownGenerator()
    b = await g.generate("Simple todo app")
    epics = b.get("epics", {})
    stories = b.get("stories", {})
    tasks = b.get("tasks", {})
    print(f"   Epics: {len(epics)}")
    print(f"   Stories: {len(stories)}")  
    print(f"   Tasks: {len(tasks)}")
    
    print("2. Saving to backlog...")
    m = BacklogManager("test_project")
    await m.initialize(epics, stories, tasks)
    print("   Done!")
    
    print("3. Checking files...")
    p = Path("/app/metagpt/workspace/projects/test_project")
    if p.exists():
        for f in p.iterdir():
            print(f"   - {f.name}")
    else:
        print(f"   Dir does not exist: {p}")

if __name__ == "__main__":
    asyncio.run(test())
