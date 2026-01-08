# agents/requirements_agent.py
class RequirementsAgent:
    def process(self, user_story):
        return f"""
        Fonctionnalité: {user_story}
        Given une condition initiale
        When une action est effectuée
        Then un résultat attendu se produit
        """
