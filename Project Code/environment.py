import random

class Environment:
    """
    Represents the home environment as a grid.
    """
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)] # 0 = Free, 1 = Obstacle
        self.locations = {} # Name -> (x, y)
        self.obstacles = set()

    def add_obstacle(self, x, y):
        """Adds an obstacle at (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 1
            self.obstacles.add((x, y))

    def add_location(self, name, x, y):
        """Adds a named location (e.g., 'Kitchen')."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.locations[name] = (x, y)

    def is_free(self, x, y):
        """Checks if a cell is free and within bounds."""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y][x] == 0)

    def get_random_free_location(self):
        """Returns a random free location (x, y)."""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.is_free(x, y):
                return (x, y)

    def print_grid(self, robot_pos=None):
        """Prints the grid to console for visualization."""
        print("  " + " ".join(str(i) for i in range(self.width)))
        for y in range(self.height):
            line = f"{y} "
            for x in range(self.width):
                if robot_pos and robot_pos == (x, y):
                    line += "R " # Robot
                elif (x, y) in self.obstacles:
                    line += "# " # Obstacle
                else:
                    # Check if it's a named location
                    loc_char = "."
                    for name, pos in self.locations.items():
                        if pos == (x, y):
                            loc_char = name[0] # First letter of location
                            break
                    line += f"{loc_char} "
            print(line)
