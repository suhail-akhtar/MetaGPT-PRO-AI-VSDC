#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/09
@Author  : MetaGPT-Pro Team
@File    : schemas.py
@Desc    : Pydantic schemas for the conversation module
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class ConversationStatus(str, Enum):
    """Status of a conversation session"""
    ACTIVE = "active"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ABANDONED = "abandoned"


class ConversationMessage(BaseModel):
    """A single message in the conversation"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class EnhancedRequirements(BaseModel):
    """Structured requirements generated from conversation"""
    project_name: str = ""
    original_idea: str = ""
    core_features: List[str] = Field(default_factory=list)
    user_stories: List[str] = Field(default_factory=list)
    technical_assumptions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    clarifying_questions: List[str] = Field(default_factory=list)
    platform: str = ""
    programming_language: str = ""


class ConversationSession(BaseModel):
    """A conversation session with AI Product Manager"""
    id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:12]}")
    initial_idea: str
    messages: List[ConversationMessage] = Field(default_factory=list)
    status: ConversationStatus = ConversationStatus.ACTIVE
    enhanced_requirements: Optional[EnhancedRequirements] = None
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# Request/Response schemas for API

class ConversationStartRequest(BaseModel):
    """Request to start a new conversation"""
    initial_idea: str


class ConversationStartResponse(BaseModel):
    """Response after starting a conversation"""
    conversation_id: str
    first_question: str
    status: str


class ConversationMessageRequest(BaseModel):
    """Request to send a message in a conversation"""
    conversation_id: str
    message: str


class ConversationMessageResponse(BaseModel):
    """Response after sending a message"""
    ai_response: str
    enhanced_requirements: Optional[EnhancedRequirements] = None
    status: str
    requires_approval: bool = False


class ConversationEnhanceRequest(BaseModel):
    """Request to enhance current requirements"""
    conversation_id: str
    current_input: Optional[str] = None


class ConversationEnhanceResponse(BaseModel):
    """Response with enhanced requirements"""
    enhanced_prd: EnhancedRequirements
    clarifying_questions: List[str] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    """Request to approve requirements"""
    conversation_id: str


class ApprovalResponse(BaseModel):
    """Response after approval"""
    project_id: str
    status: str
    message: str


class ConversationHistoryResponse(BaseModel):
    """Response with full conversation history"""
    conversation_id: str
    messages: List[ConversationMessage]
    status: str
    enhanced_requirements: Optional[EnhancedRequirements] = None
