# agents/test_agent.py
class TestAgent:
    def process(self, code):
        tests = """
        def test_example():
            assert True
        """
        with open("test_generated_code.py", "w") as f:
            f.write(tests)
        return tests
