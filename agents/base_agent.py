from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class LLMError(RuntimeError):
    pass


@dataclass
class LLMConfig:
    base_url: str
    api_key: str
    model: str = "gpt-4o-mini"
    timeout_s: int = 90
    max_retries: int = 2


class OpenAICompatibleClient:
    """
    Client minimal OpenAI-compatible (works for OpenAI OR GitHub Models if endpoint is compatible).
    Uses: POST {base_url}/chat/completions
    """
    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        url = self.cfg.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": temperature,
        }

        last_err: Optional[Exception] = None
        for attempt in range(self.cfg.max_retries + 1):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.cfg.timeout_s)
                if resp.status_code >= 400:
                    raise LLMError(f"LLM HTTP {resp.status_code}: {resp.text[:500]}")
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                last_err = e
                # backoff simple
                time.sleep(0.6 * (attempt + 1))

        raise LLMError(f"LLM call failed after retries: {last_err}")


def load_llm_config_from_env() -> LLMConfig:
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()

    if not base_url or not api_key:
        raise ValueError(
            "Missing LLM config. Please set LLM_BASE_URL and LLM_API_KEY in .env or environment."
        )
    return LLMConfig(base_url=base_url, api_key=api_key, model=model)


class BaseAgent:
    """
    Base class for agents: provides system prompt + helper methods for structured outputs.
    """

    def __init__(self, name: str, role: str, goal: str, backstory: str, client: OpenAICompatibleClient):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.client = client

    def system_prompt(self) -> str:
        return (
            f"You are {self.name}.\n"
            f"ROLE: {self.role}\n"
            f"GOAL: {self.goal}\n"
            f"CONTEXT: {self.backstory}\n"
            "Be concise, correct, and produce outputs in the requested format.\n"
        )

    def ask(self, user_prompt: str, temperature: float = 0.2) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_prompt},
        ]
        try:
            return self.client.chat(messages, temperature=temperature)
        except Exception as e:
            # 🔴 FALLBACK OFFLINE
            print(f"[WARN] LLM unavailable ({e}). Using MOCK response.")
            return self.mock_response(user_prompt)


    def mock_response(self, user_prompt: str) -> str:
                # === MOCK REQUIREMENTS AGENT ===
                if "Transform this user story" in user_prompt:
                    return """
        {
        "title": "User Management API",
        "summary": "CRUD API for managing users",
        "scope": {
            "in": ["Create user", "List users", "Update user", "Delete user"],
            "out": ["Authentication"]
        },
        "functional_requirements": [
            "Create a user",
            "List users",
            "Update a user",
            "Delete a user"
        ],
        "non_functional_requirements": [
            "Readable code",
            "Fast response"
        ],
        "entities": [
            {
            "name": "User",
            "fields": [
                {"name": "id", "type": "int", "required": true},
                {"name": "name", "type": "str", "required": true},
                {"name": "email", "type": "str", "required": true}
            ]
            }
        ],
        "api_endpoints": [
            {"method": "POST", "path": "/users", "description": "Create user"},
            {"method": "GET", "path": "/users", "description": "List users"}
        ],
        "acceptance_criteria_gherkin": [
            {
            "feature": "Create user",
            "scenario": "User is created",
            "given": ["API running"],
            "when": ["POST /users"],
            "then": ["User stored"]
            }
        ],
        "tech_choice": {
            "language": "python",
            "framework": "fastapi",
            "test_framework": "pytest"
        }
        }
        """

                # === MOCK CODE AGENT ===
                if "Generate a minimal FastAPI project" in user_prompt:
                    return """
        {
        "files": [
            {
            "path": "app/main.py",
            "content": "from fastapi import FastAPI\\nfrom app.routes import router\\n\\napp = FastAPI()\\napp.include_router(router)"
            },
            {
            "path": "app/models.py",
            "content": "from pydantic import BaseModel\\n\\nclass User(BaseModel):\\n    id: int\\n    name: str\\n    email: str"
            },
            {
            "path": "app/routes.py",
            "content": "from fastapi import APIRouter\\nfrom app.models import User\\n\\nrouter = APIRouter()\\nusers = []\\n\\n@router.post('/users')\\ndef create_user(user: User):\\n    users.append(user)\\n    return user\\n\\n@router.get('/users')\\ndef list_users():\\n    return users"
            },
            {
            "path": "requirements.txt",
            "content": "fastapi\\nuvicorn\\npytest"
            }
        ]
        }
        """

                # === MOCK TEST AGENT ===
                if "Generate pytest tests" in user_prompt:
                    return """
        {
        "files": [
            {
            "path": "tests/test_api.py",
            "content": "from fastapi.testclient import TestClient\\nfrom app.main import app\\n\\nclient = TestClient(app)\\n\\ndef test_create_user():\\n    r = client.post('/users', json={'id':1,'name':'A','email':'a@test.com'})\\n    assert r.status_code == 200\\n\\ndef test_list_users():\\n    r = client.get('/users')\\n    assert r.status_code == 200"
            }
        ]
        }
        """
                return "{}"


    def ask_json(self, user_prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Tries hard to return valid JSON object.
        """
        strict_prompt = (
            user_prompt
            + "\n\nIMPORTANT: Return ONLY a valid JSON object. No markdown. No code fences."
        )
        text = self.ask(strict_prompt, temperature=temperature).strip()

        # Try direct parse
        try:
            return json.loads(text)
        except Exception:
            # Fallback: attempt to extract first {...}
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                snippet = text[start : end + 1]
                return json.loads(snippet)

        raise ValueError(f"{self.name} returned non-JSON output: {text[:400]}")
