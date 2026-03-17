class CSP:
    """
    Constraint Satisfaction Problem solver for Task Scheduling.
    """
    def __init__(self, variables, domains):
        self.variables = variables # List of tasks
        self.domains = domains     # Dict: Task -> List of possible time slots
        self.constraints = []      # List of constraint functions

    def add_constraint(self, constraint_func):
        """Adds a constraint function (assignment -> bool)."""
        self.constraints.append(constraint_func)

    def is_consistent(self, assignment):
        """Checks if the current assignment satisfies all constraints."""
        for constraint in self.constraints:
            if not constraint(assignment):
                return False
        return True

    def backtracking_search(self, assignment={}):
        """
        Recursive Backtracking Search to find a valid assignment.
        """
        # If assignment is complete, return it
        if len(assignment) == len(self.variables):
            return assignment

        # Select unassigned variable (MRV heuristic could be used here)
        unassigned = [v for v in self.variables if v not in assignment]
        var = unassigned[0]

        for value in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            
            if self.is_consistent(new_assignment):
                result = self.backtracking_search(new_assignment)
                if result is not None:
                    return result
        
        return None

# Helper constraints
def all_different_time_constraint(assignment):
    """Constraint: No two tasks can happen at the same time."""
    times = list(assignment.values())
    return len(times) == len(set(times))

def precedence_constraint(task1, task2):
    """Returns a constraint function ensuring task1 happens before task2."""
    def check(assignment):
        if task1 in assignment and task2 in assignment:
            return assignment[task1] < assignment[task2]
        return True
    return check
