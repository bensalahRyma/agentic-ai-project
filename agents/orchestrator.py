# agents/orchestrator.py
class Orchestrator:
    def __init__(self, req_agent, code_agent, test_agent):
        self.req_agent = req_agent
        self.code_agent = code_agent
        self.test_agent = test_agent

    def run(self, user_story):
        specs = self.req_agent.process(user_story)
        code = self.code_agent.process(specs)
        tests = self.test_agent.process(code)
        return {
            "specs": specs,
            "code": code,
            "tests": tests
        }
