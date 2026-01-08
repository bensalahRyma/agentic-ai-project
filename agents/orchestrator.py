from __future__ import annotations

import os
from typing import Any, Dict, Optional


class Orchestrator:
    """
    Orchestrator:
    - Receives user story
    - Calls RequirementsAgent -> spec
    - Calls CodeAgent -> code files
    - Calls TestAgent -> test files
    - Saves everything to disk
    """

    def __init__(self, requirements_agent, code_agent, test_agent, project_root: str):
        self.requirements_agent = requirements_agent
        self.code_agent = code_agent
        self.test_agent = test_agent
        self.project_root = project_root

    def run(self, user_story: str) -> Dict[str, Any]:
        # 1) Requirements
        spec = self.requirements_agent.generate_spec(user_story)

        # 2) Code
        code_files = self.code_agent.generate_code_files(spec)
        code_written = self.code_agent.save_files(code_files, self.project_root)

        # 3) Tests
        test_files = self.test_agent.generate_tests(spec, code_files)
        tests_written = self.test_agent.save_files(test_files, self.project_root)

        return {
            "spec": spec,
            "code_written": code_written,
            "tests_written": tests_written,
        }
