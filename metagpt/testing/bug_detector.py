#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/10
@Author  : MetaGPT-Pro Team
@File    : bug_detector.py
@Desc    : Parse test output and extract bug information
"""
import re
from typing import List, Optional
from metagpt.logs import logger
from metagpt.testing.schemas import Bug, BugSeverity, BugSource


class BugDetector:
    """Parse test output and extract failures as bugs"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BugDetector, cls).__new__(cls)
        return cls._instance
    
    def extract_bugs(self, test_output: str, project_id: str = "") -> List[Bug]:
        """
        Parse test output and create bugs for failures.
        
        Supports: pytest, unittest formats
        """
        bugs = []
        
        # Try pytest format first
        pytest_bugs = self._parse_pytest(test_output, project_id)
        if pytest_bugs:
            bugs.extend(pytest_bugs)
            return bugs
        
        # Try unittest format
        unittest_bugs = self._parse_unittest(test_output, project_id)
        if unittest_bugs:
            bugs.extend(unittest_bugs)
        
        return bugs
    
    def _parse_pytest(self, output: str, project_id: str) -> List[Bug]:
        """Parse pytest output"""
        bugs = []
        
        # Pattern: FAILED tests/test_file.py::test_name - ErrorType: message
        failed_pattern = r'FAILED\s+(\S+)::(\S+)\s*[-:]\s*(.+)'
        matches = re.findall(failed_pattern, output, re.MULTILINE)
        
        for file_path, test_name, error in matches:
            severity = self._classify_severity(error)
            bug = Bug(
                title=f"Test failure: {test_name}",
                description=f"Test {test_name} in {file_path} failed",
                severity=severity,
                source=BugSource.AUTO_TEST,
                file_path=file_path,
                test_name=test_name,
                error_trace=error[:1000],
                created_by="TestRunner"
            )
            bugs.append(bug)
            logger.info(f"Detected bug from pytest: {bug.id} - {bug.title}")
        
        # Also check for ERROR pattern
        error_pattern = r'ERROR\s+(\S+)::(\S+)'
        error_matches = re.findall(error_pattern, output)
        
        for file_path, test_name in error_matches:
            # Skip if already captured as FAILED
            existing = [b for b in bugs if b.test_name == test_name]
            if existing:
                continue
            
            bug = Bug(
                title=f"Test error: {test_name}",
                description=f"Test {test_name} encountered an error",
                severity=BugSeverity.HIGH,
                source=BugSource.AUTO_TEST,
                file_path=file_path,
                test_name=test_name,
                created_by="TestRunner"
            )
            bugs.append(bug)
        
        return bugs
    
    def _parse_unittest(self, output: str, project_id: str) -> List[Bug]:
        """Parse unittest output"""
        bugs = []
        
        # Pattern: FAIL: test_name (module.TestClass)
        fail_pattern = r'FAIL:\s+(\w+)\s+\(([^)]+)\)'
        matches = re.findall(fail_pattern, output)
        
        for test_name, module in matches:
            bug = Bug(
                title=f"Test failure: {test_name}",
                description=f"unittest {test_name} in {module} failed",
                severity=BugSeverity.MEDIUM,
                source=BugSource.AUTO_TEST,
                file_path=module.replace('.', '/') + '.py',
                test_name=test_name,
                created_by="TestRunner"
            )
            bugs.append(bug)
        
        return bugs
    
    def _classify_severity(self, error: str) -> BugSeverity:
        """Quick severity classification based on error type"""
        error_lower = error.lower()
        
        # Critical patterns
        if any(p in error_lower for p in ['crash', 'segfault', 'memory', 'secur', 'injection', 'overflow']):
            return BugSeverity.CRITICAL
        
        # High patterns  
        if any(p in error_lower for p in ['assert', 'exception', 'error', 'failed', 'typeerror', 'valueerror']):
            return BugSeverity.HIGH
        
        # Medium patterns
        if any(p in error_lower for p in ['warning', 'deprecat', 'timeout']):
            return BugSeverity.MEDIUM
        
        return BugSeverity.LOW
    
    def create_bug_from_exception(
        self,
        exception: Exception,
        file_path: str = "",
        test_name: str = ""
    ) -> Bug:
        """Create a bug from a caught exception"""
        import traceback
        
        error_trace = traceback.format_exc()
        severity = self._classify_severity(str(exception))
        
        bug = Bug(
            title=f"{type(exception).__name__}: {str(exception)[:50]}",
            description=str(exception),
            severity=severity,
            source=BugSource.AUTO_TEST,
            file_path=file_path,
            test_name=test_name,
            error_trace=error_trace[:2000],
            created_by="ExceptionHandler"
        )
        
        logger.info(f"Created bug from exception: {bug.id}")
        return bug


# Global singleton
bug_detector = BugDetector()
