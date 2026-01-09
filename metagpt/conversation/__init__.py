#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/09
@Author  : MetaGPT-Pro Team
@File    : __init__.py
@Desc    : Conversation module for pre-project requirements engineering
"""
from metagpt.conversation.conversation_manager import ConversationManager, conversation_manager
from metagpt.conversation.requirement_enhancer import RequirementEnhancer
from metagpt.conversation.approval_workflow import ApprovalWorkflow
from metagpt.conversation.schemas import (
    ConversationSession,
    ConversationStartRequest,
    ConversationMessageRequest,
    EnhancedRequirements,
    ApprovalResponse,
)

__all__ = [
    "ConversationManager",
    "conversation_manager",
    "RequirementEnhancer",
    "ApprovalWorkflow",
    "ConversationSession",
    "ConversationStartRequest",
    "ConversationMessageRequest",
    "EnhancedRequirements",
    "ApprovalResponse",
]
