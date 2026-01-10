# Document Versioning API

## Overview

Track all artifact changes, enable version comparison, support rollback, maintain audit trail.

**Base URL:** `http://localhost:8000/v1/project/{project_id}`

---

## Endpoints

### List Versions

**`GET /document/{doc_type}/versions?doc_id=main_prd`**

```json
{
  "document_id": "main_prd",
  "versions": [3, 2, 1],
  "current": 3,
  "total": 3
}
```

---

### Get Version Details

**`GET /document/{doc_type}/version/{version_num}?doc_id=main_prd`**

```json
{
  "version": 2,
  "content": { "title": "Calculator App", "features": [...] },
  "changed_by": "Client",
  "change_reason": "Added multiplication feature",
  "timestamp": "2026-01-10T02:55:00",
  "changes_summary": ["Added multiplication"]
}
```

---

### Compare Versions (Diff)

**`GET /document/{doc_type}/diff?doc_id=main_prd&v1=1&v2=3`**

```json
{
  "document_id": "main_prd",
  "v1": 1,
  "v2": 3,
  "summary": "~3 modified",
  "added": [],
  "removed": [],
  "modified": [
    { "field": "title", "old": "Calculator App", "new": "Calculator App Pro" },
    { "field": "features", "old": "[2 items]", "new": "[4 items]" }
  ],
  "is_json_diff": true
}
```

---

### Rollback

**`POST /document/{doc_type}/rollback?doc_id=main_prd`**

```json
// Request
{ "version": 1, "reason": "Client wants original version" }

// Response
{
  "rolled_back": true,
  "from_version": 3,
  "to_version": 1,
  "new_current": 4
}
```

> **Note:** Rollback creates a NEW version (v4) with old content. History is preserved.

---

### Create Snapshot

**`POST /document/{doc_type}/snapshot`**

```json
// Query params
doc_id=main_prd
content={"title":"New PRD",...}
changed_by=Alice
reason=Updated requirements

// Response
{
  "version": 5,
  "document_id": "main_prd",
  "document_type": "prd",
  "timestamp": "2026-01-10T03:00:00"
}
```

---

### Project History

**`GET /history?limit=100`**

```json
{
  "timeline": [
    {
      "id": "chg_abc123",
      "timestamp": "2026-01-10T03:00:00",
      "document_id": "main_prd",
      "document_type": "prd",
      "version": 4,
      "changed_by": "Client",
      "change_reason": "Rollback to v1",
      "changes_summary": "Restored content from version 1"
    }
  ],
  "total_changes": 4
}
```

---

## Document Types

| Type | Description |
|------|-------------|
| `prd` | Product Requirements Document |
| `design` | Architecture/Design docs |
| `code` | Source code files |

---

## Data Storage

```
workspace/projects/{project_id}/
  └─ versions/
      ├─ prd/
      │   └─ main_prd/
      │       ├─ v1.json
      │       ├─ v2.json
      │       ├─ v3.json
      │       ├─ v4.json
      │       └─ current.txt  # "4"
      └─ design/
          └─ ...
```
