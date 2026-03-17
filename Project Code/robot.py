import random

class Robot:
    """
    Simulates a home service robot.
    """
    def __init__(self, name, start_pos, environment):
        self.name = name
        self.position = start_pos
        self.environment = environment
        self.battery = 100
        self.holding_item = None
        self.path = []

    def sense_obstacles(self):
        """
        Simulates sensing nearby obstacles.
        Returns a list of adjacent obstacles.
        """
        x, y = self.position
        obstacles = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # Check if out of bounds or is an obstacle
            if not self.environment.is_free(nx, ny):
                obstacles.append((nx, ny))
        return obstacles

    def move(self, next_pos):
        """
        Attempts to move to next_pos.
        Includes uncertainty: 10% chance to fail move.
        Consumes battery.
        """
        if self.battery <= 0:
            print(f"{self.name}: Battery dead! Cannot move.")
            return False

        # Uncertainty removed for smoother demo


        if self.environment.is_free(next_pos[0], next_pos[1]):
            self.position = next_pos
            self.battery -= 1
            print(f"{self.name}: Moved to {self.position}. Battery: {self.battery}%")
            return True
        else:
            print(f"{self.name}: Path blocked at {next_pos}!")
            return False

    def pick_item(self, item):
        """Picks up an item if at the same location."""
        print(f"{self.name}: Picking up {item}...")
        self.holding_item = item

    def drop_item(self):
        """Drops the currently held item."""
        if self.holding_item:
            print(f"{self.name}: Delivered {self.holding_item}!")
            self.holding_item = None
        else:
            print(f"{self.name}: Nothing to drop.")

    def charge(self):
        """Recharges battery to 100%."""
        print(f"{self.name}: Charging...")
        self.battery = 100
