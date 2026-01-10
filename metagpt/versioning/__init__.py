#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : __init__.py
@Desc    : Document Versioning & History module
"""
from metagpt.versioning.schemas import DocumentVersion, VersionHistory, ChangeEntry
from metagpt.versioning.version_manager import VersionManager, version_manager
from metagpt.versioning.diff_generator import DiffGenerator
from metagpt.versioning.rollback_handler import RollbackHandler

__all__ = [
    "DocumentVersion",
    "VersionHistory",
    "ChangeEntry",
    "VersionManager",
    "version_manager",
    "DiffGenerator",
    "RollbackHandler",
]
