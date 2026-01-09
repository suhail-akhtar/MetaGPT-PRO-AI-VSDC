import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.config2 import config

router = APIRouter()

def get_workspace_root() -> Path:
    # Use config workspace path or default
    return Path(config.workspace.path) if config.workspace.path else DEFAULT_WORKSPACE_ROOT

@router.get("/tree")
async def list_files(path: str = ""):
    """List files in the workspace (directory tree)"""
    root = get_workspace_root()
    target = root / path
    
    # Security check
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied: Path outside workspace.")
    
    if not target.exists():
         raise HTTPException(status_code=404, detail="Path not found.")
    
    if not target.is_dir():
        return {"type": "file", "name": target.name, "size": target.stat().st_size}
        
    items = []
    for item in target.iterdir():
        items.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size": item.stat().st_size if item.is_file() else 0
        })
    return {"path": str(path), "items": items}

@router.get("/content")
async def get_file_content(path: str):
    """Read file content"""
    root = get_workspace_root()
    target = root / path
    
    # Security check
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied: Path outside workspace.")
        
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
        
    try:
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        return {"path": path, "content": content}
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Cannot read binary file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
