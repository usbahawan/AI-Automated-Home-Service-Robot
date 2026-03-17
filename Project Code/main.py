import time
from environment import Environment
from robot import Robot
from knowledge_base import KnowledgeBase
from csp import CSP, all_different_time_constraint, precedence_constraint
from planner import HierarchicalPlanner

def main():
    print("=== Intelligent Home Service Robot Simulation ===\n")

    # 1. Setup Environment
    print("--- Initializing Environment ---")
    env = Environment(width=10, height=10)
    
    # Add Locations
    env.add_location('Kitchen', 0, 0)
    env.add_location('LivingRoom', 8, 8)
    env.add_location('Charger', 0, 9)
    env.add_location('Bedroom', 9, 0)
    
    # Add Obstacles (Simple wall)
    for y in range(3, 7):
        env.add_obstacle(4, y)
    
    env.print_grid()
    print("\n")

    # 2. Setup Robot
    print("--- Initializing Robot ---")
    robot = Robot("RoboHelper", (0, 9), env) # Start at Charger
    print(f"Robot started at {robot.position} with {robot.battery}% battery.\n")

    # 3. Knowledge Base Demo
    print("--- Knowledge Base Reasoning ---")
    kb = KnowledgeBase()
    kb.add_fact("BatteryLow")
    
    # Rule: If BatteryLow -> ShouldCharge
    kb.add_rule(lambda facts: "BatteryLow" in facts, "ShouldCharge")
    
    kb.forward_chaining()
    if kb.query("ShouldCharge"):
        print("Reasoning Result: Robot needs to charge!\n")
        robot.charge()

    # 4. CSP Task Scheduling Demo
    print("--- CSP Task Scheduling ---")
    tasks = ['CleanKitchen', 'ServeTea', 'Charge']
    domains = {
        'CleanKitchen': [1, 2, 3],
        'ServeTea': [1, 2, 3],
        'Charge': [1, 2, 3]
    }
    
    scheduler = CSP(tasks, domains)
    scheduler.add_constraint(all_different_time_constraint)
    # Constraint: Charge must happen before ServeTea (just as an example)
    scheduler.add_constraint(precedence_constraint('Charge', 'ServeTea'))
    
    schedule = scheduler.backtracking_search()
    print(f"Generated Schedule: {schedule}")
    
    # Sort tasks by time
    sorted_tasks = sorted(schedule.items(), key=lambda x: x[1])
    print(f"Execution Order: {[t[0] for t in sorted_tasks]}\n")

    # 5. Hierarchical Planning & Execution
    print("--- Executing Plan: Serve Tea ---")
    planner = HierarchicalPlanner(robot, env)
    
    # Goal: Deliver Tea to LivingRoom
    # Note: In a full system, the 'ServeTea' task from CSP would trigger this goal.
    goal = ('deliver', 'tea', 'LivingRoom')
    
    success = planner.plan_and_execute(goal)
    
    if success:
        print("\n=== Mission Accomplished! ===")
    else:
        print("\n=== Mission Failed! ===")

    print("\nFinal Environment State:")
    env.print_grid(robot.position)

if __name__ == "__main__":
    main()
