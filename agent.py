from collections import deque
import heapq
import random

class SearchAgent:
    """An agent that uses uninformed search strategies (BFS, DFS, UCS) to navigate the grid and collect food."""

    def __init__(self, active_algo='BFS'):
        self.plan = []
        self.active_algo = active_algo
        self.pos = (0, 0)

    def sense_and_act(self, percept: dict) -> str:
        # Check if self.plan is empty
        if not self.plan:
            all_food = percept.get('all_food', [])
            width, height = percept.get('grid_size', (10, 10))
            walls = set(tuple(w) for w in percept.get('walls', []))

            if not all_food:
                return random.choice(['Up', 'Down', 'Left', 'Right'])

            # Find the closest food pellet from percept['all_food']
            closest_food = min(all_food, key=lambda f: abs(self.pos[0] - f[0]) + abs(self.pos[1] - f[1]))
            target_food = tuple(closest_food)

            # Execute the search method matching self.active_algo
            algo = self.active_algo.upper()
            if algo == 'BFS':
                path_coords = self.bfs_search(self.pos, target_food, width, height, walls)
            elif algo == 'DFS':
                path_coords = self.dfs_search(self.pos, target_food, width, height, walls)
            elif algo == 'UCS':
                path_coords = self.ucs_search(self.pos, target_food, width, height, walls)
            else:
                path_coords = self.bfs_search(self.pos, target_food, width, height, walls)

            # Store the resulting sequence of actions in self.plan
            if path_coords and len(path_coords) > 1:
                self.plan = self.coords_to_actions(path_coords)
            else:
                return random.choice(['Up', 'Down', 'Left', 'Right'])

        # Return the first action from the plan using return self.plan.pop(0)
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
            x2, y2 = path_coords[i+1]
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
        # FIFO queue using deque (Graph Search with reached set)
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
        # LIFO stack using standard list (Graph Search with reached set)
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
        # Priority Queue ordered by path cost g(n) (Graph Search with reached set)
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