#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : __init__.py
@Desc    : Agent Collaboration Layer module
"""
from metagpt.collaboration.schemas import (
    AgentMessage,
    MessageType,
    ConversationThread,
    ThreadStatus,
    AgentInbox,
    ApprovalRequest,
    ApprovalStatus,
)
from metagpt.collaboration.agent_messenger import AgentMessenger, messenger
from metagpt.collaboration.collaboration_log import CollaborationLog
from metagpt.collaboration.approval_gates import ApprovalGates, approval_gates

__all__ = [
    "AgentMessage",
    "MessageType",
    "ConversationThread",
    "ThreadStatus",
    "AgentInbox",
    "ApprovalRequest",
    "ApprovalStatus",
    "AgentMessenger",
    "messenger",
    "CollaborationLog",
    "ApprovalGates",
    "approval_gates",
]
