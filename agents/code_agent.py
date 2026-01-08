from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple

from agents.base_agent import BaseAgent


class CodeAgent(BaseAgent):
    """
    Input: spec JSON
    Output: dict of generated files {path: content}
    Saves files to disk.
    """

    def generate_code_files(self, spec: Dict[str, Any]) -> Dict[str, str]:
        spec_pretty = json.dumps(spec, indent=2, ensure_ascii=False)

        prompt = f"""
You are generating a small but clean codebase for the given spec.

SPEC JSON:
{spec_pretty}

Generate a minimal FastAPI project with:
- app/main.py (FastAPI app)
- app/models.py (Pydantic models)
- app/storage.py (in-memory storage or SQLite if very simple)
- app/routes.py (API routes)
- requirements.txt
- README_generated.md (how to run)

Constraints:
- Keep it simple and runnable.
- Use Pydantic models.
- Provide CRUD for main entity.
- Code must be complete, no placeholders like TODO.
- Return JSON object: {{ "files": [{{"path":"...","content":"..."}}, ...] }}
- No markdown. Only JSON.
"""
        data = self.ask_json(prompt, temperature=0.2)

        files = data.get("files", [])
        out: Dict[str, str] = {}
        for f in files:
            path = f["path"].strip()
            content = f["content"]
            out[path] = content
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
