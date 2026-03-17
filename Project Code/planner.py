from search import a_star_search

class HierarchicalPlanner:
    """
    Hierarchical Planner that decomposes goals into subtasks and executes them.
    """
    def __init__(self, robot, environment):
        self.robot = robot
        self.environment = environment

    def plan_and_execute(self, high_level_goal, search_algorithm=a_star_search):
        """
        Decomposes a high-level goal and executes subtasks.
        Example Goal: ('deliver', 'tea', 'living_room')
        """
        print(f"\nPlanner: Received goal {high_level_goal}")
        
        subtasks = self.decompose_goal(high_level_goal)
        print(f"Planner: Decomposed into subtasks: {subtasks}")
        
        for task in subtasks:
            success = self.execute_subtask(task, search_algorithm)
            if not success:
                print("Planner: Plan failed!")
                return False
        
        print("Planner: Goal completed successfully!")
        return True

    def decompose_goal(self, goal):
        """
        Decomposes goals into primitive actions.
        """
        action, item, target_loc_name = goal
        
        subtasks = []
        
        # 1. Navigate to item location (e.g., Kitchen for tea)
        # Ideally this knowledge comes from KB, hardcoded here for simplicity
        item_location_name = 'Kitchen' 
        subtasks.append(('navigate', item_location_name))
        
        # 2. Pick item
        subtasks.append(('pick', item))
        
        # 3. Navigate to target location
        subtasks.append(('navigate', target_loc_name))
        
        # 4. Drop item
        subtasks.append(('drop', item))
        
        return subtasks

    def execute_subtask(self, task, search_algorithm=a_star_search):
        """
        Executes a single primitive subtask.
        """
        action = task[0]
        
        if action == 'navigate':
            target_name = task[1]
            target_pos = self.environment.locations.get(target_name)
            
            if not target_pos:
                print(f"Planner: Unknown location {target_name}")
                return False
                
            print(f"Planner: Navigating to {target_name} {target_pos}...")
            path = search_algorithm(self.environment, self.robot.position, target_pos)
            
            if not path:
                print("Planner: No path found!")
                return False
                
            # Execute path
            for next_pos in path:
                if next_pos == self.robot.position: continue # Skip start
                if not self.robot.move(next_pos):
                    # Simple replanning: try one more time or fail
                    print("Planner: Movement failed, retrying...")
                    if not self.robot.move(next_pos):
                        print("Planner: Retry failed.")
                        return False
            return True
            
        elif action == 'pick':
            item = task[1]
            self.robot.pick_item(item)
            return True
            
        elif action == 'drop':
            self.robot.drop_item()
            return True
            
        return False
