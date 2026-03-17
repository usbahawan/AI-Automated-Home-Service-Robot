class KnowledgeBase:
    """
    Simple Knowledge Base using propositional logic concepts.
    Stores facts and rules.
    """
    def __init__(self):
        self.facts = set()
        self.rules = [] # List of (condition_func, action_fact)

    def add_fact(self, fact):
        """Adds a fact to the KB."""
        self.facts.add(fact)
        print(f"KB: Added fact '{fact}'")

    def remove_fact(self, fact):
        """Removes a fact from the KB."""
        if fact in self.facts:
            self.facts.remove(fact)

    def add_rule(self, condition_func, action_fact):
        """
        Adds a rule: IF condition_func() is True THEN add action_fact.
        """
        self.rules.append((condition_func, action_fact))

    def query(self, fact):
        """Checks if a fact exists in the KB."""
        return fact in self.facts

    def forward_chaining(self):
        """
        Applies rules to derive new facts until no new facts can be added.
        """
        new_facts_added = True
        while new_facts_added:
            new_facts_added = False
            for condition, result in self.rules:
                if result not in self.facts and condition(self.facts):
                    self.add_fact(result)
                    new_facts_added = True
                    print(f"KB: Rule triggered! Derived '{result}'")

# Example usage helpers
def fact_exists(fact):
    return lambda facts: fact in facts
