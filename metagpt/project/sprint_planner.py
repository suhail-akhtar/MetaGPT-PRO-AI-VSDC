#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : sprint_planner.py
@Desc    : Organizes tasks into sprints
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from metagpt.logs import logger
from metagpt.project.schemas import Sprint, Task, Story, TaskStatus, Priority


class SprintPlanner:
    DEFAULT_SPRINT_DAYS = 7
    DEFAULT_VELOCITY = 20
    
    def __init__(self, sprint_duration: int = None, velocity: int = None):
        self.sprint_duration = sprint_duration or self.DEFAULT_SPRINT_DAYS
        self.velocity = velocity or self.DEFAULT_VELOCITY
    
    def create_sprints(self, tasks: Dict[str, Task], stories: Dict[str, Story], start_date: datetime = None) -> List[Sprint]:
        if not start_date:
            start_date = datetime.now()
        
        sorted_tasks = self._sort_tasks(tasks, stories)
        
        sprints = []
        current_sprint_tasks = []
        current_points = 0
        sprint_number = 1
        
        for task in sorted_tasks:
            if current_points + task.story_points > self.velocity and current_sprint_tasks:
                sprint = self._create_sprint(sprint_number, current_sprint_tasks, start_date + timedelta(days=(sprint_number - 1) * self.sprint_duration))
                sprints.append(sprint)
                sprint_number += 1
                current_sprint_tasks = []
                current_points = 0
            
            current_sprint_tasks.append(task)
            current_points += task.story_points
        
        if current_sprint_tasks:
            sprint = self._create_sprint(sprint_number, current_sprint_tasks, start_date + timedelta(days=(sprint_number - 1) * self.sprint_duration))
            sprints.append(sprint)
        
        logger.info(f"Created {len(sprints)} sprints from {len(tasks)} tasks")
        return sprints
    
    def _sort_tasks(self, tasks: Dict[str, Task], stories: Dict[str, Story]) -> List[Task]:
        task_priority = {}
        for task in tasks.values():
            if task.parent_story and task.parent_story in stories:
                priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
                task_priority[task.id] = priority_order.get(stories[task.parent_story].priority, 2)
            else:
                task_priority[task.id] = 2
        
        def sort_key(task: Task):
            is_foundation = any(kw in task.title.lower() for kw in ["setup", "structure", "init"])
            return (not is_foundation, len(task.depends_on) > 0, task_priority.get(task.id, 2), task.story_points)
        
        return sorted(tasks.values(), key=sort_key)
    
    def _create_sprint(self, number: int, tasks: List[Task], start_date: datetime) -> Sprint:
        total_points = sum(t.story_points for t in tasks)
        name = f"Sprint {number}: {'Foundation' if number == 1 else 'Feature Development'}"
        goals = [f"Complete: {t.title}" for t in tasks[:3]]
        
        return Sprint(
            number=number,
            name=name,
            duration_days=self.sprint_duration,
            start_date=start_date,
            end_date=start_date + timedelta(days=self.sprint_duration),
            goals=goals,
            tasks=[t.id for t in tasks],
            total_points=total_points,
            completed_points=0
        )
