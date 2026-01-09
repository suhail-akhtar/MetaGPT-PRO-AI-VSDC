#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : task_breakdown.py
@Desc    : Converts approved requirements into Epics, Stories, and Tasks
"""
from typing import List, Dict
from metagpt.logs import logger
from metagpt.config2 import config
from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.project.schemas import Epic, Story, Task, TaskType, Priority


TASK_BREAKDOWN_PROMPT = """You are an experienced Agile Project Manager. Break down the following requirements into structured work items.

## Requirements
{requirements}

## Instructions
Create:
1. **Epics**: High-level features (2-4 epics)
2. **Stories**: User stories for each epic (2-4 per epic)
3. **Tasks**: Implementation tasks for each story (2-5 per story)

Assign story_points (1, 2, 3, 5, 8, 13) and assigned_to ("Alice" for docs, "Bob" for design, "Alex" for code).

Output JSON:
```json
{{
  "epics": [
    {{
      "title": "Epic title",
      "description": "Brief description",
      "stories": [
        {{
          "title": "As a user, I want...",
          "priority": "high",
          "story_points": 5,
          "tasks": [
            {{"title": "Task", "story_points": 2, "assigned_to": "Alex"}}
          ]
        }}
      ]
    }}
  ]
}}
```
"""


class TaskBreakdownGenerator:
    def __init__(self):
        self._llm = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = create_llm_instance(config.llm)
        return self._llm
    
    async def generate(self, requirements: str) -> Dict[str, Dict]:
        llm = self._get_llm()
        prompt = TASK_BREAKDOWN_PROMPT.format(requirements=requirements)
        
        try:
            response = await llm.aask(prompt)
            import json
            import re
            
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            json_str = json_match.group(1) if json_match else response
            data = json.loads(json_str)
            return self._convert_to_models(data)
        except Exception as e:
            logger.exception(f"Task breakdown failed: {e}")
            return self._generate_fallback(requirements)
    
    def _convert_to_models(self, data: dict) -> Dict[str, Dict]:
        epics, stories, tasks = {}, {}, {}
        
        for epic_data in data.get("epics", []):
            epic = Epic(title=epic_data["title"], description=epic_data.get("description", ""))
            
            for story_data in epic_data.get("stories", []):
                story = Story(
                    title=story_data["title"],
                    priority=Priority(story_data.get("priority", "medium")),
                    story_points=story_data.get("story_points", 5)
                )
                
                for task_data in story_data.get("tasks", []):
                    task = Task(
                        title=task_data["title"],
                        story_points=task_data.get("story_points", 2),
                        assigned_to=task_data.get("assigned_to", "Alex"),
                        parent_story=story.id
                    )
                    tasks[task.id] = task
                    story.tasks.append(task.id)
                
                stories[story.id] = story
                epic.stories.append(story.id)
            
            epics[epic.id] = epic
        
        logger.info(f"Generated: {len(epics)} epics, {len(stories)} stories, {len(tasks)} tasks")
        return {"epics": epics, "stories": stories, "tasks": tasks}
    
    def _generate_fallback(self, requirements: str) -> Dict[str, Dict]:
        epic = Epic(title="Project Implementation", description=requirements[:200])
        story = Story(title="Implement core functionality", priority=Priority.HIGH, story_points=8)
        
        tasks_list = [
            Task(title="Setup project structure", story_points=2, assigned_to="Alex", parent_story=story.id),
            Task(title="Implement main features", story_points=5, assigned_to="Alex", parent_story=story.id),
            Task(title="Add tests", story_points=3, assigned_to="Alex", parent_story=story.id)
        ]
        
        tasks = {t.id: t for t in tasks_list}
        story.tasks = [t.id for t in tasks_list]
        epic.stories = [story.id]
        
        return {"epics": {epic.id: epic}, "stories": {story.id: story}, "tasks": tasks}
