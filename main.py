from agents.orchestrator import Orchestrator
from agents.requirements_agent import RequirementsAgent
from agents.code_agent import CodeAgent
from agents.test_agent import TestAgent

orchestrator = Orchestrator(
    RequirementsAgent(),
    CodeAgent(),
    TestAgent()
)

result = orchestrator.run(
    "En tant qu’utilisateur, je veux créer un compte"
)

print(result)
