# agents/base_agent.py
from crewai import Agent

class BaseAgent:
    def __init__(self, name, role, goal, backstory):
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False
        )