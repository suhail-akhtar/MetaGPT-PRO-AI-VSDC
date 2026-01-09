# Sprint/Backlog System API

## Overview

The Project API provides sprint planning, backlog management, and Kanban board tracking for MetaGPT projects.

**Base URL:** `http://localhost:8000/v1/project`

---

## Endpoints

### Get Sprints

**`GET /{project_id}/sprints`**

```json
{
  "sprints": [...],
  "current_sprint": 1,
  "total_sprints": 2
}
```

---

### Get Sprint Details

**`GET /{project_id}/sprint/{num}`**

```json
{
  "sprint_num": 1,
  "name": "Sprint 1: Foundation",
  "tasks": [...],
  "progress": 45,
  "goals": ["Setup project", "Implement core"]
}
```

---

### Get Backlog

**`GET /{project_id}/backlog`**

```json
{
  "stories": [...],
  "total_points": 34,
  "priority_order": ["STORY-001", "STORY-002"]
}
```

---

### Get Kanban Board

**`GET /{project_id}/board`**

```json
{
  "todo": [...],
  "in_progress": [...],
  "review": [...],
  "testing": [...],
  "done": [...],
  "blocked": [...]
}
```

---

### Move Task

**`POST /{project_id}/task/move`**

```json
// Request
{
  "task_id": "TASK-001",
  "new_status": "in_progress"
}

// Response
{
  "updated": true,
  "task_id": "TASK-001",
  "new_status": "in_progress"
}
```

---

### Get Metrics

**`GET /{project_id}/metrics`**

```json
{
  "project_id": "calc_app",
  "current_sprint": 1,
  "progress_percent": 65,
  "velocity": 12,
  "blocked_count": 0
}
```

---

### WebSocket: Board Stream

**`WS /{project_id}/board/stream`**

Events:
- `task_moved`: Task status changed
- `initial_state`: Board state on connect
