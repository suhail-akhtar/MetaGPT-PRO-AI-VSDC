#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : diff_generator.py
@Desc    : Generate diffs between document versions
"""
import json
import difflib
from typing import Dict, List, Any, Union
from metagpt.logs import logger
from metagpt.versioning.schemas import DocumentVersion, DiffResult


class DiffGenerator:
    """Generate diffs between document versions"""
    
    def compare(
        self,
        v1: DocumentVersion,
        v2: DocumentVersion
    ) -> DiffResult:
        """
        Compare two versions and generate diff.
        Auto-detects content type (JSON vs text).
        """
        is_json = isinstance(v1.content, dict) and isinstance(v2.content, dict)
        
        if is_json:
            return self._json_diff(v1, v2)
        else:
            return self._text_diff(v1, v2)
    
    def _json_diff(self, v1: DocumentVersion, v2: DocumentVersion) -> DiffResult:
        """Generate diff for JSON/dict content"""
        old = v1.content if isinstance(v1.content, dict) else {}
        new = v2.content if isinstance(v2.content, dict) else {}
        
        added = []
        removed = []
        modified = []
        
        # Find added and modified
        for key, value in new.items():
            if key not in old:
                added.append(f"{key}: {self._summarize_value(value)}")
            elif old[key] != value:
                modified.append({
                    "field": key,
                    "old": self._summarize_value(old[key]),
                    "new": self._summarize_value(value)
                })
        
        # Find removed
        for key in old:
            if key not in new:
                removed.append(f"{key}: {self._summarize_value(old[key])}")
        
        return DiffResult(
            document_id=v1.document_id,
            v1=v1.version,
            v2=v2.version,
            added=added,
            removed=removed,
            modified=modified,
            is_json_diff=True
        )
    
    def _text_diff(self, v1: DocumentVersion, v2: DocumentVersion) -> DiffResult:
        """Generate diff for text content"""
        old_text = str(v1.content) if v1.content else ""
        new_text = str(v2.content) if v2.content else ""
        
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)
        
        differ = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"v{v1.version}",
            tofile=f"v{v2.version}",
            lineterm=""
        )
        
        raw_diff = "".join(differ)
        
        # Parse diff for summary
        added = []
        removed = []
        
        for line in raw_diff.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                added.append(line[1:].strip()[:100])
            elif line.startswith("-") and not line.startswith("---"):
                removed.append(line[1:].strip()[:100])
        
        return DiffResult(
            document_id=v1.document_id,
            v1=v1.version,
            v2=v2.version,
            added=added[:20],  # Limit for display
            removed=removed[:20],
            modified=[],
            is_json_diff=False,
            raw_diff=raw_diff
        )
    
    def _summarize_value(self, value: Any) -> str:
        """Summarize a value for display"""
        if isinstance(value, str):
            return value[:100] + "..." if len(value) > 100 else value
        elif isinstance(value, list):
            return f"[{len(value)} items]"
        elif isinstance(value, dict):
            return f"{{{len(value)} fields}}"
        else:
            return str(value)[:100]
    
    def generate_summary(self, diff: DiffResult) -> str:
        """Generate human-readable summary of diff"""
        parts = []
        
        if diff.added:
            parts.append(f"+{len(diff.added)} added")
        if diff.removed:
            parts.append(f"-{len(diff.removed)} removed")
        if diff.modified:
            parts.append(f"~{len(diff.modified)} modified")
        
        if not parts:
            return "No changes"
        
        return ", ".join(parts)
