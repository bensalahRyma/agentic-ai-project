import os
from dotenv import load_dotenv

from agents.base_agent import OpenAICompatibleClient, load_llm_config_from_env
from agents.base_agent import BaseAgent
from agents.requirements_agent import RequirementsAgent
from agents.code_agent import CodeAgent
from agents.test_agent import TestAgent
from agents.orchestrator import Orchestrator


def build_agents():
    cfg = load_llm_config_from_env()
    client = OpenAICompatibleClient(cfg)

    req = RequirementsAgent(
        name="RequirementsAgent",
        role="Business analyst / requirements engineer",
        goal="Turn vague user stories into implementable specs and acceptance criteria",
        backstory="You are rigorous and pragmatic. You produce clear requirements and Gherkin scenarios.",
        client=client,
    )

    code = CodeAgent(
        name="CodeAgent",
        role="Senior backend engineer",
        goal="Generate a small, clean FastAPI codebase from a spec",
        backstory="You write correct, runnable Python code with good structure and minimal complexity.",
        client=client,
    )

    tests = TestAgent(
        name="TestAgent",
        role="QA engineer",
        goal="Generate reliable pytest tests for the generated API",
        backstory="You cover CRUD and edge cases using FastAPI TestClient.",
        client=client,
    )

    return req, code, tests


def main():
    load_dotenv()

    project_root = os.path.dirname(os.path.abspath(__file__))

    user_story = """
En tant qu'utilisateur,
je veux une API REST pour gérer des utilisateurs
afin de pouvoir créer, consulter, modifier et supprimer des utilisateurs.
Chaque utilisateur a: id, name, email.
"""

    req, code, tests = build_agents()
    orchestrator = Orchestrator(req, code, tests, project_root=project_root)

    result = orchestrator.run(user_story)

    print("\n✅ DONE")
    print("Files created:")
    for p in result["code_written"]:
        print(" -", p)
    for p in result["tests_written"]:
        print(" -", p)


if __name__ == "__main__":
    main()
