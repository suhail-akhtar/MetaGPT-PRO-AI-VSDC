from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ProjectRequest(BaseModel):
    """Request to synthesize a new project/requirement"""
    requirement: str
    project_name: Optional[str] = None
    conversation_id: Optional[str] = None  # If provided, uses pre-approved requirements
    investment: float = 3.0
    n_round: int = 5

class ConfigUpdate(BaseModel):
    """Request to update configuration"""
    llm: Optional[Dict[str, Any]] = None
    other: Optional[Dict[str, Any]] = None

class RoleStatus(BaseModel):
    """Status of a single role"""
    name: str
    profile: str
    goal: str
    is_idle: bool
    current_todo: Optional[str] = None

class CompanyStatus(BaseModel):
    """Overall status of the virtual company"""
    status: str  # idle, running, paused
    roles: List[RoleStatus]
    is_idle: bool
