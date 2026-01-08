from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """
    Input: spec + generated code files
    Output: pytest tests (API tests using TestClient)
    """

    def generate_tests(self, spec: Dict[str, Any], generated_files: Dict[str, str]) -> Dict[str, str]:
        spec_pretty = json.dumps(spec, indent=2, ensure_ascii=False)

        # keep only key files to avoid huge prompt
        key_files = {k: v for k, v in generated_files.items() if k in ["app/main.py", "app/routes.py", "app/models.py"]}
        key_pretty = json.dumps(key_files, indent=2, ensure_ascii=False)

        prompt = f"""
Generate pytest tests for a FastAPI app following this spec.

SPEC:
{spec_pretty}

KEY CODE FILES (for context):
{key_pretty}

Requirements:
- Use fastapi.testclient.TestClient
- Create tests for: create, read list, read by id, update, delete
- Include at least 2 edge cases (invalid payload, missing id, etc.)
- Return JSON object: {{ "files": [{{"path":"tests/test_api.py","content":"..."}}, ...] }}
- No markdown. Only JSON.
"""
        data = self.ask_json(prompt, temperature=0.2)
        files = data.get("files", [])
        out: Dict[str, str] = {}
        for f in files:
            out[f["path"].strip()] = f["content"]
        return out

    def save_files(self, files: Dict[str, str], root_dir: str) -> List[str]:
        written: List[str] = []
        for rel_path, content in files.items():
            abs_path = os.path.join(root_dir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as fp:
                fp.write(content)
            written.append(rel_path)
        return written
