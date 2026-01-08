# agents/code_agent.py
class CodeAgent:
    def process(self, specs):
        code = "# Code généré automatiquement\n\ndef example():\n    pass"
        with open("generated_code.py", "w") as f:
            f.write(code)
        return code
