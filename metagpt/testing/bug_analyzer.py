#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : bug_analyzer.py
@Desc    : LLM-based bug severity classification
"""
from metagpt.logs import logger
from metagpt.testing.schemas import Bug, BugSeverity, BugPriority


class BugAnalyzer:
    """Analyze bugs using LLM for severity classification"""
    
    SEVERITY_PROMPT = """Analyze this bug and classify its severity.

Bug Title: {title}
Description: {description}
Error: {error_trace}
File: {file_path}

Severity levels:
- critical: Crash, data loss, security vulnerability, system down
- high: Major feature broken, blocks users, no workaround
- medium: Minor feature issue, workaround exists
- low: UI glitch, typo, cosmetic

Respond with ONLY one word: critical, high, medium, or low"""
    
    def __init__(self):
        self._llm = None
    
    def _get_llm(self):
        if self._llm is None:
            from metagpt.provider.llm_provider_registry import create_llm_instance
            from metagpt.config2 import config
            self._llm = create_llm_instance(config.llm)
        return self._llm
    
    async def classify_severity(self, bug: Bug) -> BugSeverity:
        """Use LLM to classify bug severity"""
        try:
            llm = self._get_llm()
            prompt = self.SEVERITY_PROMPT.format(
                title=bug.title,
                description=bug.description,
                error_trace=bug.error_trace[:500],
                file_path=bug.file_path
            )
            
            response = await llm.aask(prompt)
            severity_str = response.strip().lower()
            
            # Map to enum
            mapping = {
                "critical": BugSeverity.CRITICAL,
                "high": BugSeverity.HIGH,
                "medium": BugSeverity.MEDIUM,
                "low": BugSeverity.LOW
            }
            
            severity = mapping.get(severity_str, BugSeverity.MEDIUM)
            logger.info(f"LLM classified bug {bug.id} as {severity.value}")
            return severity
            
        except Exception as e:
            logger.warning(f"LLM severity classification failed: {e}, using rule-based")
            return self._rule_based_severity(bug)
    
    def _rule_based_severity(self, bug: Bug) -> BugSeverity:
        """Fallback rule-based classification"""
        error_lower = (bug.error_trace + bug.description + bug.title).lower()
        
        # Critical patterns
        critical_patterns = ['crash', 'segfault', 'memory leak', 'security', 
                           'injection', 'overflow', 'corruption', 'data loss']
        if any(p in error_lower for p in critical_patterns):
            return BugSeverity.CRITICAL
        
        # High patterns
        high_patterns = ['exception', 'error', 'failed', 'broken', 'cannot', 
                        'unable', 'null', 'undefined', 'typeerror']
        if any(p in error_lower for p in high_patterns):
            return BugSeverity.HIGH
        
        # Low patterns
        low_patterns = ['typo', 'style', 'format', 'spacing', 'color', 'font']
        if any(p in error_lower for p in low_patterns):
            return BugSeverity.LOW
        
        return BugSeverity.MEDIUM
    
    def determine_priority(self, severity: BugSeverity, sprint_active: bool = True) -> BugPriority:
        """Determine priority based on severity and context"""
        if severity == BugSeverity.CRITICAL:
            return BugPriority.P0  # Interrupt current work
        elif severity == BugSeverity.HIGH:
            return BugPriority.P1 if sprint_active else BugPriority.P2
        elif severity == BugSeverity.MEDIUM:
            return BugPriority.P2
        else:
            return BugPriority.P3
    
    def determine_assignee(self, bug: Bug) -> str:
        """Determine which agent should fix the bug"""
        file_path = bug.file_path.lower()
        error = (bug.error_trace + bug.description).lower()
        
        # Architecture/design issues -> Bob
        if any(p in file_path for p in ['design', 'architect', 'schema', 'model']):
            return "Bob"
        if any(p in error for p in ['design', 'architecture', 'structure']):
            return "Bob"
        
        # Requirements issues -> Alice
        if any(p in error for p in ['requirement', 'spec', 'undefined feature']):
            return "Alice"
        
        # Default: code bugs -> Alex
        return "Alex"


# Usage example in bug creation flow:
# analyzer = BugAnalyzer()
# severity = await analyzer.classify_severity(bug)
# priority = analyzer.determine_priority(severity)
# assignee = analyzer.determine_assignee(bug)
