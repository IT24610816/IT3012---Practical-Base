from collections import deque
import heapq
import math
import random
from logic_engine import KnowledgeBase


class SearchAgent:
    """An agent that uses search strategies (BFS, DFS, UCS, A*) to navigate the grid and collect food."""

    def __init__(self, active_algo='AStar'):
        self.plan = []
        self.active_algo = active_algo
        self.pos = (0, 0)
        
        # Instantiate the Knowledge Base
        self.kb = KnowledgeBase()
        
        # Define Safety Rules (Horn Clauses)
        # Rule 1: TargetVisible ∧ HasDust ⇒ SafeToEngage
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        
        # Rule 2: SafeToEngage ∧ BloodseekerMissing ⇒ Retreat
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    # Step 1.1: Heuristic Functions
    def manhattan_distance(self, pos, goal):
        """Calculates h(n) = |x1 - x2| + |y1 - y2| returning an integer."""
        x1, y1 = pos
        x2, y2 = goal
        return int(abs(x1 - x2) + abs(y1 - y2))

    def euclidean_distance(self, pos, goal):
        """Calculates h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)."""
        x1, y1 = pos
        x2, y2 = goal
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # Step 1.2: A* Search Implementation
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        width, height = grid_size
        frontier = []
        reached_states = set()

        # Calculate initial heuristic value
        if heuristic_type.lower() == 'euclidean':
            h_start = self.euclidean_distance(start_pos, goal_pos)
        else:
            h_start = self.manhattan_distance(start_pos, goal_pos)

        # Priority queue tuple: (f_cost, g_cost, current_pos, path_taken)
        g_start = 0
        f_start = g_start + h_start
        heapq.heappush(frontier, (f_start, g_start, start_pos, [start_pos]))

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            for neighbor, _ in self.get_neighbors(current_pos, width, height, walls):
                if neighbor not in reached_states:
                    
                    # --- Step 3.2: Knowledge Base Feasibility Check ---
                    self.kb.clear_facts()
                    
                    if neighbor == goal_pos:  
                        self.kb.tell_fact('TargetVisible')
                        self.kb.tell_fact('HasDust')

                    self.kb.forward_chain()

                    # If 'Retreat' is deduced, mark tile as Infeasible and skip it
                    if 'Retreat' in self.kb.facts:
                        continue

                    g_new = g_cost + 1

                    if heuristic_type.lower() == 'euclidean':
                        h_new = self.euclidean_distance(neighbor, goal_pos)
                    else:
                        h_new = self.manhattan_distance(neighbor, goal_pos)

                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, g_new, neighbor, path_taken + [neighbor]))

        return []

    # Step 1.3: Decision Loop Integration
    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            # Extract state representations from the percept dictionary
            all_food = percept.get('all_food', percept.get('remaining_food', []))
            width, height = percept.get('grid_size', (10, 10))
            walls = set(tuple(w) for w in percept.get('walls', []))

            # Handle edge case where all_food might be an integer count instead of a list
            if isinstance(all_food, int):
                all_food = percept.get('all_food', [])

            if not all_food:
                return random.choice(['Up', 'Down', 'Left', 'Right'])

            # Target the closest food item
            closest_food = min(all_food, key=lambda f: self.manhattan_distance(self.pos, f))
            target_food = tuple(closest_food)

            algo = self.active_algo.upper()
            if algo in ('ASTAR', 'A*'):
                path_coords = self.astar_search(self.pos, target_food, walls, (width, height), heuristic_type='manhattan')
            elif algo == 'BFS':
                path_coords = self.bfs_search(self.pos, target_food, width, height, walls)
            elif algo == 'DFS':
                path_coords = self.dfs_search(self.pos, target_food, width, height, walls)
            elif algo == 'UCS':
                path_coords = self.ucs_search(self.pos, target_food, width, height, walls)
            else:
                path_coords = self.astar_search(self.pos, target_food, walls, (width, height))

            if path_coords and len(path_coords) > 1:
                self.plan = self.coords_to_actions(path_coords)
            else:
                return random.choice(['Up', 'Down', 'Left', 'Right'])

        if self.plan:
            action = self.plan.pop(0)
            self.update_pos(action)
            return action

        return random.choice(['Up', 'Down', 'Left', 'Right'])

    def update_pos(self, action):
        x, y = self.pos
        if action == 'Up':
            y += 1
        elif action == 'Down':
            y -= 1
        elif action == 'Left':
            x -= 1
        elif action == 'Right':
            x += 1
        self.pos = (x, y)

    def get_neighbors(self, pos, width, height, walls):
        x, y = pos
        neighbors = []
        for action, (dx, dy) in [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                neighbors.append(((nx, ny), action))
        return neighbors

    def coords_to_actions(self, path_coords):
        actions = []
        for i in range(len(path_coords) - 1):
            x1, y1 = path_coords[i]
            x2, y2 = path_coords[i + 1]
            if x2 == x1 + 1 and y2 == y1:
                actions.append('Right')
            elif x2 == x1 - 1 and y2 == y1:
                actions.append('Left')
            elif x2 == x1 and y2 == y1 + 1:
                actions.append('Up')
            elif x2 == x1 and y2 == y1 - 1:
                actions.append('Down')
        return actions

    def bfs_search(self, start, goal, width, height, walls):
        frontier = deque([(start, [start])])
        reached = {start}

        while frontier:
            current, path = frontier.popleft()
            if current == goal:
                return path

            for neighbor, _ in self.get_neighbors(current, width, height, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    frontier.append((neighbor, path + [neighbor]))
        return []

    def dfs_search(self, start, goal, width, height, walls):
        frontier = [(start, [start])]
        reached = {start}

        while frontier:
            current, path = frontier.pop()
            if current == goal:
                return path

            for neighbor, _ in self.get_neighbors(current, width, height, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    frontier.append((neighbor, path + [neighbor]))
        return []

    def ucs_search(self, start, goal, width, height, walls):
        frontier = [(0, start, [start])]
        reached = {}

        while frontier:
            cost, current, path = heapq.heappop(frontier)

            if current == goal:
                return path

            if current in reached and reached[current] <= cost:
                continue
            reached[current] = cost

            for neighbor, _ in self.get_neighbors(current, width, height, walls):
                new_cost = cost + 1
                if neighbor not in reached or new_cost < reached[neighbor]:
                    reached[neighbor] = new_cost
                    heapq.heappush(frontier, (new_cost, neighbor, path + [neighbor]))
        return []


# Step 1.1 Testing Checkpoint
if __name__ == "__main__":
    test_agent = SearchAgent()
    mock_start = (0, 0)
    mock_goal = (3, 4)

    m_val = test_agent.manhattan_distance(mock_start, mock_goal)
    e_val = test_agent.euclidean_distance(mock_start, mock_goal)

    print("\n--- Testing Checkpoint ---")
    print(f"Manhattan Distance (0,0) to (3,4): {m_val} (Expected: 7)")
    print(f"Euclidean Distance (0,0) to (3,4): {e_val} (Expected: 5.0)")
    print("\n")