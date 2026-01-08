from __future__ import annotations

from typing import Any, Dict

from agents.base_agent import BaseAgent


class RequirementsAgent(BaseAgent):
    """
    Input: vague user story
    Output: structured spec JSON + acceptance criteria (Gherkin)
    """

    def generate_spec(self, user_story: str) -> Dict[str, Any]:
        prompt = f"""
Transform this user story into a clear, structured software specification.

USER STORY:
{user_story}

Return JSON with this schema:
{{
  "title": "short title",
  "summary": "1-3 sentences",
  "scope": {{
    "in": ["..."],
    "out": ["..."]
  }},
  "functional_requirements": ["..."],
  "non_functional_requirements": ["..."],
  "entities": [
    {{
      "name": "EntityName",
      "fields": [{{"name":"id","type":"str/int","required":true}}, ...]
    }}
  ],
  "api_endpoints": [
    {{
      "method":"GET/POST/PUT/DELETE",
      "path":"/...",
      "description":"...",
      "request_body_example": {{}},
      "response_example": {{}}
    }}
  ],
  "acceptance_criteria_gherkin": [
    {{
      "feature":"...",
      "scenario":"...",
      "given":["..."],
      "when":["..."],
      "then":["..."]
    }}
  ],
  "tech_choice": {{
    "language":"python",
    "framework":"fastapi",
    "test_framework":"pytest"
  }}
}}

Rules:
- Keep it implementable in a small demo.
- Prefer FastAPI CRUD in-memory or SQLite (simple).
- Provide at least 3 endpoints (CRUD).
"""
        return self.ask_json(prompt, temperature=0.2)
