import heapq
from collections import deque

class Node:
    """
    Represents a node in the search graph.
    """
    def __init__(self, position, parent=None, g=0, h=0):
        self.position = position
        self.parent = parent
        self.g = g # Cost from start to current node
        self.h = h # Heuristic cost from current node to goal
        self.f = g + h # Total cost

    def __lt__(self, other):
        """Comparison for priority queue (min-heap) based on f cost."""
        return self.f < other.f

def heuristic(a, b):
    """
    Manhattan distance heuristic for grid navigation.
    h(n) = |x1 - x2| + |y1 - y2|
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(environment, node):
    """Returns valid neighbors (up, down, left, right) for a given node."""
    x, y = node.position
    neighbors = []
    # Directions: Up, Down, Left, Right
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if environment.is_free(nx, ny):
            neighbors.append((nx, ny))
            
    return neighbors

def reconstruct_path(node):
    """Backtracks from the goal node to the start to reconstruct the path."""
    path = []
    current = node
    while current:
        path.append(current.position)
        current = current.parent
    return path[::-1] # Return reversed path (Start -> Goal)

def a_star_search(environment, start, goal):
    """
    A* Search Algorithm.
    Finds the shortest path from start to goal using f(n) = g(n) + h(n).
    """
    open_list = []
    closed_set = set()
    
    start_node = Node(start, None, 0, heuristic(start, goal))
    heapq.heappush(open_list, start_node)
    
    print(f"Starting A* Search from {start} to {goal}...")
    
    while open_list:
        current_node = heapq.heappop(open_list)
        
        if current_node.position == goal:
            print("Goal reached!")
            return reconstruct_path(current_node)
            
        closed_set.add(current_node.position)
        
        for neighbor_pos in get_neighbors(environment, current_node):
            if neighbor_pos in closed_set:
                continue
                
            g_cost = current_node.g + 1 # Assuming uniform cost of 1 per move
            h_cost = heuristic(neighbor_pos, goal)
            neighbor_node = Node(neighbor_pos, current_node, g_cost, h_cost)
            
            # Check if neighbor is already in open list with a lower g cost
            # (Simplified for grid: just add to heap, duplicates handled by closed_set check on pop usually, 
            # but here we just push. For strict optimization we'd check existing.)
            heapq.heappush(open_list, neighbor_node)
            
    print("No path found.")
    return None

def bfs_search(environment, start, goal):
    """
    Breadth-First Search (BFS).
    Explores all neighbors at the current depth before moving to the next level.
    Guarantees shortest path in unweighted graphs.
    """
    queue = deque([Node(start)])
    visited = set([start])
    
    print(f"Starting BFS Search from {start} to {goal}...")
    
    while queue:
        current_node = queue.popleft()
        
        if current_node.position == goal:
            print("Goal reached!")
            return reconstruct_path(current_node)
            
        for neighbor_pos in get_neighbors(environment, current_node):
            if neighbor_pos not in visited:
                visited.add(neighbor_pos)
                queue.append(Node(neighbor_pos, current_node))
                
    print("No path found.")
    return None

def dfs_search(environment, start, goal):
    """
    Depth-First Search (DFS).
    Explores as far as possible along each branch before backtracking.
    Does NOT guarantee shortest path.
    """
    stack = [Node(start)]
    visited = set([start])
    
    print(f"Starting DFS Search from {start} to {goal}...")
    
    while stack:
        current_node = stack.pop()
        
        if current_node.position == goal:
            print("Goal reached!")
            return reconstruct_path(current_node)
            
        for neighbor_pos in get_neighbors(environment, current_node):
            if neighbor_pos not in visited:
                visited.add(neighbor_pos)
                stack.append(Node(neighbor_pos, current_node))
                
    print("No path found.")
    return None

def ucs_search(environment, start, goal):
    """
    Uniform Cost Search (UCS).
    Explores nodes based on path cost g(n). 
    Equivalent to A* with h(n) = 0.
    """
    open_list = []
    closed_set = set()
    
    # Priority Queue stores tuples: (cost, node)
    # Using Node structure similar to A* but h=0
    start_node = Node(start, None, 0, 0)
    heapq.heappush(open_list, start_node)
    
    print(f"Starting UCS Search from {start} to {goal}...")
    
    while open_list:
        current_node = heapq.heappop(open_list)
        
        if current_node.position == goal:
            print("Goal reached!")
            return reconstruct_path(current_node)
            
        closed_set.add(current_node.position)
        
        for neighbor_pos in get_neighbors(environment, current_node):
            if neighbor_pos in closed_set:
                continue
                
            g_cost = current_node.g + 1 # Uniform cost
            neighbor_node = Node(neighbor_pos, current_node, g_cost, 0) # h=0 for UCS
            
            # Simplified: just push to heap. 
            # In a strict implementation, we would check if we found a shorter path to an existing node in open_list
            heapq.heappush(open_list, neighbor_node)
            
    print("No path found.")
    return None

def greedy_bfs_search(environment, start, goal):
    """
    Greedy Best-First Search.
    Explores nodes based on heuristic cost h(n) ONLY.
    f(n) = h(n).
    """
    open_list = []
    closed_set = set()
    
    # Priority Queue stores tuples: (cost, node)
    # f = h(n), g is ignored (or 0) for priority
    h_start = heuristic(start, goal)
    start_node = Node(start, None, 0, h_start)
    # Start node f = h
    start_node.f = h_start 
    heapq.heappush(open_list, start_node)
    
    print(f"Starting Greedy BFS Search from {start} to {goal}...")
    
    while open_list:
        current_node = heapq.heappop(open_list)
        
        if current_node.position == goal:
            print("Goal reached!")
            return reconstruct_path(current_node)
            
        closed_set.add(current_node.position)
        
        for neighbor_pos in get_neighbors(environment, current_node):
            if neighbor_pos in closed_set:
                continue
                
            h_cost = heuristic(neighbor_pos, goal)
            # g_cost is irrelevant for sorting, but we can track it
            g_cost = current_node.g + 1 
            
            neighbor_node = Node(neighbor_pos, current_node, g_cost, h_cost)
            # Crucial: Greedy BFS uses f = h
            neighbor_node.f = h_cost
            
            heapq.heappush(open_list, neighbor_node)
            
    print("No path found.")
    return None
